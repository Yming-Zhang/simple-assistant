#!/usr/bin/env python3
"""
单独测试按键唤醒功能
"""

import time
from wake.key_detector import get_key_detector
from audio.tts import speak


def main():
    print("=" * 50)
    print("按键唤醒测试")
    print("=" * 50)
    print("\n按 Cmd+Shift+Space 来触发唤醒")
    print("按 Ctrl+C 退出\n")
    
    wake_count = 0
    
    def on_wake():
        nonlocal wake_count
        wake_count += 1
        print(f"\n✅ 按键唤醒成功！(第 {wake_count} 次)")
        message = "Ai bot is ready, please say something."
        speak(message)
        print("等待下一次唤醒...\n")
    
    detector = get_key_detector()
    detector.start(on_wake)
    
    try:
        while detector.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n收到退出信号...")
    finally:
        detector.stop()
        print(f"\n测试结束，共唤醒 {wake_count} 次")


if __name__ == "__main__":
    main()
