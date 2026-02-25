import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio.microphone import record_audio
from audio.player import play_audio


def main():
    print("=" * 50)
    print("音频测试")
    print("=" * 50)
    
    test_file = "test_output.wav"
    
    try:
        record_audio(test_file, seconds=5)
        print()
        play_audio(test_file)
        print()
        print("测试成功！")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
