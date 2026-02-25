import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio.microphone import record_audio
from audio.stt import transcribe


def main():
    print("=" * 50)
    print("STT 语音转文字测试")
    print("=" * 50)
    
    test_file = "test_stt.wav"
    
    try:
        print("\n步骤 1: 录音 5 秒...")
        print("请对着麦克风说话...")
        record_audio(test_file, seconds=5)
        
        print("\n步骤 2: 语音转文字...")
        text = transcribe(test_file)
        
        print("\n" + "=" * 50)
        print(f"识别结果: {text}")
        print("=" * 50)
        print("\n测试成功！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
