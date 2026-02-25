#!/usr/bin/env python3
"""
唤醒系统测试脚本
测试按键唤醒和语音唤醒功能
"""

import time
from wake.wake_system import get_wake_system
from audio.tts import speak


def main():
    print("=" * 50)
    print("唤醒系统测试")
    print("=" * 50)
    
    wake_count = 0
    
    def on_wake():
        nonlocal wake_count
        wake_count += 1
        print(f"\n🎉 第 {wake_count} 次唤醒成功！")
        
        message = f"我在，第 {wake_count} 次唤醒"
        print(f"反馈: {message}")
        speak(message)
        print("\n等待下一次唤醒... (按 Ctrl+C 退出)\n")
    
    wake_system = get_wake_system()
    
    print("\n可用的唤醒方式:")
    print("  1. 按键唤醒: Cmd+Shift+Space (始终可用)")
    print("  2. 语音唤醒: 'hey computer' (需要配置 WAKE_ACCESS_KEY)")
    print("\n开始监听...\n")
    
    wake_system.start(on_wake, enable_voice=True, enable_key=True)
    
    try:
        while wake_system.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n收到退出信号...")
    finally:
        wake_system.stop()
        print(f"\n测试结束，共唤醒 {wake_count} 次")


if __name__ == "__main__":
    main()
