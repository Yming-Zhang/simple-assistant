import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio.tts import speak, save_to_file


def main():
    print("=" * 50)
    print("TTS 文字转语音测试")
    print("=" * 50)
    
    test_text = "你好，这是一个测试。文字转语音功能正常工作！"
    
    print(f"\n测试文字: {test_text}")
    print("\n步骤 1: 播放语音...")
    speak(test_text)
    
    print("\n步骤 2: 保存语音到文件...")
    output_file = "test_tts_output.aiff"
    save_to_file(test_text, output_file)
    
    print("\n" + "=" * 50)
    print("测试成功！")
    print("=" * 50)


if __name__ == "__main__":
    main()
