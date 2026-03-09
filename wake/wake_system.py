from typing import Callable, Optional
from wake.key_detector import KeyDetector, get_key_detector
from wake.voice_detector import VoiceDetector, get_voice_detector


class WakeSystem:
    def __init__(
        self,
        key_detector: Optional[KeyDetector] = None,
        voice_detector: Optional[VoiceDetector] = None
    ):
        self.key_detector = key_detector or get_key_detector()
        self.voice_detector = voice_detector or get_voice_detector()
        self.callback: Optional[Callable] = None
        # 记录最近一次唤醒来源: 'voice' | 'key' | 'manual'
        self._last_wake_source: str = "manual"

    @property
    def last_wake_source(self) -> str:
        """获取最近一次唤醒来源"""
        return self._last_wake_source
    
    def set_wake_source(self, source: str):
        """手动设置唤醒来源（供 bridge 等外部调用）"""
        self._last_wake_source = source

    def start(self, callback: Callable, enable_voice: bool = True, enable_key: bool = True) -> None:
        """
        启动唤醒系统
        
        Args:
            callback: 当唤醒被触发时调用的回调函数，接收 wake_source 参数
            enable_voice: 是否启用语音唤醒
            enable_key: 是否启用按键唤醒
        """
        self.callback = callback
        
        print("=" * 50)
        print("启动唤醒系统")
        print("=" * 50)
        
        if enable_key:
            self.key_detector.start(self._on_key_wake)
        
        if enable_voice:
            self.voice_detector.start(self._on_voice_wake)
        
        print("\n等待唤醒...")
        print(f"  - 按键唤醒: {self.key_detector.hotkey}")
        if self.voice_detector.access_key:
            print(f"  - 语音唤醒: '{self.voice_detector.keyword}'")
        else:
            print("  - 语音唤醒: 未配置 (需要 Access Key)")

    def _on_key_wake(self) -> None:
        """快捷键唤醒回调"""
        self._last_wake_source = "key"
        print(f"[WakeSystem] 唤醒来源: key")
        if self.callback:
            self.callback()

    def _on_voice_wake(self) -> None:
        """语音唤醒回调"""
        self._last_wake_source = "voice"
        print(f"[WakeSystem] 唤醒来源: voice")
        if self.callback:
            self.callback()

    def stop(self) -> None:
        """停止唤醒系统"""
        print("\n正在停止唤醒系统...")
        self.key_detector.stop()
        self.voice_detector.stop()
        print("唤醒系统已停止")

    def is_running(self) -> bool:
        """返回唤醒系统是否正在运行"""
        return self.key_detector.is_running() or self.voice_detector.is_running()


_wake_system_instance: Optional[WakeSystem] = None


def get_wake_system() -> WakeSystem:
    global _wake_system_instance
    if _wake_system_instance is None:
        _wake_system_instance = WakeSystem()
    return _wake_system_instance


if __name__ == "__main__":
    import time
    
    print("测试唤醒系统...")
    print("按 Cmd+Shift+Space 或说 'hey computer' (需要配置 Access Key) 来触发")
    print("按 Ctrl+C 退出\n")
    
    def on_wake():
        ws = get_wake_system()
        print(f"\n✅ 唤醒触发！来源: {ws.last_wake_source}")
        print("等待下一次唤醒...\n")
    
    wake_system = WakeSystem()
    wake_system.start(on_wake)
    
    try:
        while wake_system.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        wake_system.stop()
