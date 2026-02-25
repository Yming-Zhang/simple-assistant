import threading
from typing import Callable, Optional
import pvporcupine
import sounddevice as sd
import numpy as np
from config import config


class VoiceDetector:
    def __init__(self, access_key: Optional[str] = None, keyword: Optional[str] = None):
        self.access_key = access_key or config.wake.access_key
        self.keyword = keyword or config.wake.keyword
        self.callback: Optional[Callable] = None
        self.porcupine: Optional[pvporcupine.Porcupine] = None
        self.stream: Optional[sd.InputStream] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable) -> None:
        """
        启动语音唤醒监听
        
        Args:
            callback: 当唤醒词被检测到时调用的回调函数
        """
        if self._running:
            print("语音唤醒监听已经在运行中")
            return
        
        if not self.access_key:
            print("警告: 没有配置 Porcupine Access Key，语音唤醒功能不可用")
            print("请访问 https://console.picovoice.ai/ 获取免费的 Access Key")
            print("并在 .env 文件中设置 WAKE_ACCESS_KEY")
            return
        
        try:
            self.callback = callback
            
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=[self.keyword]
            )
            
            self._running = True
            self._thread = threading.Thread(target=self._detect_loop, daemon=True)
            self._thread.start()
            
            print(f"语音唤醒监听已启动，唤醒词: {self.keyword}")
        except Exception as e:
            print(f"启动语音唤醒监听失败: {e}")
            self._running = False
            if self.porcupine:
                self.porcupine.delete()
                self.porcupine = None

    def _detect_loop(self) -> None:
        """语音检测循环"""
        try:
            with sd.InputStream(
                channels=1,
                samplerate=self.porcupine.sample_rate,
                dtype=np.int16,
                blocksize=self.porcupine.frame_length
            ) as stream:
                while self._running:
                    pcm, _ = stream.read(self.porcupine.frame_length)
                    pcm = pcm.flatten()
                    
                    keyword_index = self.porcupine.process(pcm)
                    if keyword_index >= 0:
                        print(f"检测到唤醒词: {self.keyword}")
                        if self.callback:
                            self.callback()
        except Exception as e:
            if self._running:
                print(f"语音检测出错: {e}")

    def stop(self) -> None:
        """停止语音唤醒监听"""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        
        print("语音唤醒监听已停止")

    def is_running(self) -> bool:
        """返回监听是否正在运行"""
        return self._running


_voice_detector_instance: Optional[VoiceDetector] = None


def get_voice_detector() -> VoiceDetector:
    global _voice_detector_instance
    if _voice_detector_instance is None:
        _voice_detector_instance = VoiceDetector()
    return _voice_detector_instance


if __name__ == "__main__":
    import time
    
    print("测试语音唤醒检测器...")
    print("注意: 需要在 .env 文件中配置 WAKE_ACCESS_KEY")
    print("说 'hey computer' 来触发，或按 Ctrl+C 退出")
    
    def on_wake():
        print("✅ 语音唤醒触发！")
    
    detector = VoiceDetector()
    detector.start(on_wake)
    
    try:
        while detector.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        detector.stop()
