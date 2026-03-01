import time
from wake.voice_detector import VoiceDetector

print("测试语音唤醒系统...")
print("说 'computer' 来触发")
print("系统将在 5 秒后自动退出")

def on_wake():
    print("✅ 语音唤醒触发！")

detector = VoiceDetector()
detector.start(on_wake)

try:
    for i in range(5):
        print(f"剩余 {5-i} 秒...")
        time.sleep(1)
finally:
    detector.stop()
    print("测试完成")
