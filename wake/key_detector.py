import threading
from typing import Callable, Optional
from pynput import keyboard
from config import config


class KeyDetector:
    def __init__(self, hotkey: Optional[str] = None):
        self.hotkey = hotkey or config.wake.hotkey
        self.callback: Optional[Callable] = None
        self.listener: Optional[keyboard.Listener] = None
        self._running = False

    def start(self, callback: Callable) -> None:
        """
        启动按键监听
        
        Args:
            callback: 当热键被按下时调用的回调函数
        """
        if self._running:
            print("按键监听已经在运行中")
            return
        
        self.callback = callback
        self._running = True
        
        def on_activate():
            print(f"检测到热键: {self.hotkey}")
            if self.callback:
                self.callback()
        
        try:
            self.listener = keyboard.GlobalHotKeys({
                self.hotkey: on_activate
            })
            self.listener.start()
            print(f"按键监听已启动，热键: {self.hotkey}")
        except Exception as e:
            print(f"启动按键监听失败: {e}")
            self._running = False

    def stop(self) -> None:
        """停止按键监听"""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self._running = False
        print("按键监听已停止")

    def is_running(self) -> bool:
        """返回监听是否正在运行"""
        return self._running


_key_detector_instance: Optional[KeyDetector] = None


def get_key_detector() -> KeyDetector:
    global _key_detector_instance
    if _key_detector_instance is None:
        _key_detector_instance = KeyDetector()
    return _key_detector_instance


if __name__ == "__main__":
    import time
    
    print("测试按键检测器...")
    print("按 Cmd+Shift+Space 来触发，或按 Ctrl+C 退出")
    
    def on_wake():
        print("✅ 唤醒触发！")
    
    detector = KeyDetector()
    detector.start(on_wake)
    
    try:
        while detector.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        detector.stop()
