import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import queue
import struct
from pathlib import Path
from config import config


class AudioRecorder:
    """
    音频录制器，支持：
    - 手动控制 start/stop
    - VAD 自动停止（webrtcvad 检测 2s 连续静音后自动结束）
    """
    
    # VAD 参数
    VAD_FRAME_MS = 30           # webrtcvad 帧长度（ms），可选 10/20/30
    VAD_AGGRESSIVENESS = 2      # 0~3，越高越激进过滤非人声
    SILENCE_TIMEOUT = 2.0       # 连续静音多少秒触发自动停止
    MIN_SPEECH_DURATION = 0.3   # 至少检测到多少秒有效语音才算开始说话
    
    def __init__(self):
        self._recording = False
        self._audio_queue = queue.Queue()    # 主队列：供保存文件用
        self._vad_queue = queue.Queue()      # VAD 队列：供静音检测用
        self._sample_rate = config.audio.sample_rate  # 应为 16000
        self._channels = config.audio.channels
        self._stream = None
        
        # VAD 相关
        self._vad = None
        self._vad_callback = None           # 静音自停后的回调
        self._silence_start = None          # 开始静音的时间戳
        self._has_speech = False             # 是否检测到过人声
        self._speech_duration = 0.0          # 累计人声时长
        self._vad_monitor_thread = None
        self._use_vad = False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """音频流回调：存入队列供后续保存 + VAD 检测"""
        if status:
            print(f"音频状态: {status}")
        if self._recording:
            data = indata.copy()
            self._audio_queue.put(data)
            if self._use_vad:
                self._vad_queue.put(data)
    
    # ---- 手动控制 API（不变） ----
    
    def start_recording(self):
        """开始录音（手动模式，需手动调 stop_recording）"""
        if self._recording:
            print("已经在录音中")
            return
        
        self._recording = True
        self._audio_queue = queue.Queue()
        self._has_speech = False
        self._speech_duration = 0.0
        self._silence_start = None
        
        self._stream = sd.InputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            callback=self._audio_callback
        )
        self._stream.start()
        print("开始录音...")
    
    def stop_recording(self, output_path: str = "output.wav") -> str:
        """停止录音并保存到文件"""
        if not self._recording:
            print("没有在录音")
            return None
        
        self._recording = False
        self._vad_callback = None
        
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        
        print("录音结束，正在保存...")
        
        audio_frames = []
        while not self._audio_queue.empty():
            audio_frames.append(self._audio_queue.get())
        
        if not audio_frames:
            print("没有录制到音频")
            return None
        
        recording = np.concatenate(audio_frames, axis=0)
        output_file = Path(output_path)
        sf.write(str(output_file), recording, self._sample_rate)
        print(f"音频已保存到: {output_file.absolute()}")
        
        return str(output_file)
    
    # ---- VAD 自动停止 API ----
    
    def start_recording_with_vad(self, on_silence_stop=None):
        """
        开始录音 + VAD 静音检测。
        当连续 SILENCE_TIMEOUT 秒无人声时自动停止录音并调用 on_silence_stop(audio_path)。
        
        Args:
            on_silence_stop: 回调函数 on_silence_stop(audio_path: str | None)
        """
        import webrtcvad
        
        self._vad = webrtcvad.Vad(self.VAD_AGGRESSIVENESS)
        self._vad_callback = on_silence_stop
        self._has_speech = False
        self._speech_duration = 0.0
        self._silence_start = None
        self._use_vad = True
        
        # 清空 VAD 队列
        while not self._vad_queue.empty():
            try: self._vad_queue.get_nowait()
            except: break
        
        # 先启动普通录音
        self.start_recording()
        
        # 启动 VAD 监控线程
        self._vad_monitor_thread = threading.Thread(
            target=self._vad_monitor_loop, daemon=True
        )
        self._vad_monitor_thread.start()
        print("[VAD] 静音检测已启动")
    
    def _vad_monitor_loop(self):
        """
        VAD 监控线程：定期从音频队列读取数据并检测人声。
        独立于 sounddevice 回调，避免阻塞音频流。
        """
        import time as _time
        import webrtcvad
        
        frame_samples = int(self._sample_rate * self.VAD_FRAME_MS / 1000)
        frame_bytes = frame_samples * 2  # 16-bit PCM
        
        buffer = b""
        
        while self._recording:
            # 从 VAD 专用队列中取音频数据
            try:
                chunk = self._vad_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            
            # float32 → int16 PCM bytes
            pcm_int16 = (chunk[:, 0] * 32767).astype(np.int16)
            buffer += pcm_int16.tobytes()
            
            # 按帧处理
            while len(buffer) >= frame_bytes:
                frame = buffer[:frame_bytes]
                buffer = buffer[frame_bytes:]
                
                try:
                    is_speech = self._vad.is_speech(frame, self._sample_rate)
                except Exception:
                    continue
                
                now = _time.time()
                
                if is_speech:
                    self._speech_duration += self.VAD_FRAME_MS / 1000.0
                    self._silence_start = None
                    
                    if self._speech_duration >= self.MIN_SPEECH_DURATION:
                        self._has_speech = True
                else:
                    # 非人声帧
                    if self._has_speech and self._silence_start is None:
                        self._silence_start = now
                    
                    if (self._has_speech and self._silence_start and
                            now - self._silence_start >= self.SILENCE_TIMEOUT):
                        print(f"[VAD] 检测到 {self.SILENCE_TIMEOUT}s 静音，自动停止录音")
                        self._auto_stop()
                        return
        
        print("[VAD] 监控线程退出（录音已被外部停止）")
    
    def _auto_stop(self):
        """VAD 检测到静音超时，自动停止录音并调用回调"""
        self._use_vad = False
        audio_path = self.stop_recording("output.wav")
        
        if self._vad_callback:
            try:
                self._vad_callback(audio_path)
            except Exception as e:
                print(f"[VAD] 回调执行失败: {e}")


# ============================================================
# 全局单例 + 便捷函数
# ============================================================

_recorder = None
_recorder_lock = threading.Lock()


def get_recorder() -> AudioRecorder:
    global _recorder
    with _recorder_lock:
        if _recorder is None:
            _recorder = AudioRecorder()
        return _recorder


def start_recording():
    """开始录音（便捷函数）"""
    get_recorder().start_recording()


def stop_recording(output_path: str = "output.wav") -> str:
    """停止录音并保存（便捷函数）"""
    return get_recorder().stop_recording(output_path)


def start_recording_with_vad(on_silence_stop=None):
    """开始录音 + VAD 静音自停（便捷函数）"""
    get_recorder().start_recording_with_vad(on_silence_stop)


def record_audio(output_path: str = "output.wav", seconds: int = None) -> str:
    """兼容旧接口：固定时长录音"""
    import time
    
    if seconds is None:
        seconds = config.audio.record_seconds
    
    print(f"开始录音，时长 {seconds} 秒...")
    start_recording()
    time.sleep(seconds)
    return stop_recording(output_path)


if __name__ == "__main__":
    print("测试 VAD 录音：按回车开始，说话后静音 2s 自动停止")
    input()
    
    def on_done(path):
        print(f"自动停止，文件: {path}")
    
    start_recording_with_vad(on_done)
    
    import time
    time.sleep(30)  # 等待 VAD 自动停止
