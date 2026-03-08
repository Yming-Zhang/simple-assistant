import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import queue
from pathlib import Path
from config import config


class AudioRecorder:
    """
    支持自由控制开始/停止的音频录制器
    """
    
    def __init__(self):
        self._recording = False
        self._audio_queue = queue.Queue()
        self._sample_rate = config.audio.sample_rate
        self._channels = config.audio.channels
        self._stream = None
        self._record_thread = None
    
    def _audio_callback(self, indata, frames, time, status):
        """
        音频流回调函数，将音频数据放入队列
        """
        if status:
            print(f"音频状态: {status}")
        if self._recording:
            self._audio_queue.put(indata.copy())
    
    def start_recording(self):
        """
        开始录音
        """
        if self._recording:
            print("已经在录音中")
            return
        
        self._recording = True
        self._audio_queue = queue.Queue()
        
        # 打开音频流
        self._stream = sd.InputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            callback=self._audio_callback
        )
        
        self._stream.start()
        print("开始录音...")
    
    def stop_recording(self, output_path: str = "output.wav") -> str:
        """
        停止录音并保存到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        if not self._recording:
            print("没有在录音")
            return None
        
        self._recording = False
        
        # 停止音频流
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        
        print("录音结束，正在保存...")
        
        # 从队列中收集所有音频数据
        audio_frames = []
        while not self._audio_queue.empty():
            audio_frames.append(self._audio_queue.get())
        
        if not audio_frames:
            print("没有录制到音频")
            return None
        
        # 拼接所有音频帧
        recording = np.concatenate(audio_frames, axis=0)
        
        # 保存到文件
        output_file = Path(output_path)
        sf.write(str(output_file), recording, self._sample_rate)
        print(f"音频已保存到: {output_file.absolute()}")
        
        return str(output_file)


# 全局录音器实例
_recorder = None
_recorder_lock = threading.Lock()


def get_recorder() -> AudioRecorder:
    """
    获取全局录音器实例
    """
    global _recorder
    with _recorder_lock:
        if _recorder is None:
            _recorder = AudioRecorder()
        return _recorder


def start_recording():
    """
    开始录音（便捷函数）
    """
    recorder = get_recorder()
    recorder.start_recording()


def stop_recording(output_path: str = "output.wav") -> str:
    """
    停止录音并保存（便捷函数）
    
    Args:
        output_path: 输出文件路径
        
    Returns:
        输出文件路径
    """
    recorder = get_recorder()
    return recorder.stop_recording(output_path)


def record_audio(output_path: str = "output.wav", seconds: int = None) -> str:
    """
    兼容旧接口：固定时长录音
    
    Args:
        output_path: 输出文件路径
        seconds: 录音时长（秒）
        
    Returns:
        输出文件路径
    """
    import time
    
    if seconds is None:
        seconds = config.audio.record_seconds
    
    print(f"开始录音，时长 {seconds} 秒...")
    start_recording()
    time.sleep(seconds)
    return stop_recording(output_path)


if __name__ == "__main__":
    print("测试录音：按回车开始，再按回车停止")
    input()
    start_recording()
    input()
    stop_recording("test_recording.wav")
