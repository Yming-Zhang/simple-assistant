import soundfile as sf
import sounddevice as sd
from pathlib import Path


def play_audio(file_path: str) -> None:
    """
    播放 WAV 音频文件
    
    Args:
        file_path: 音频文件路径
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    print(f"正在播放: {file.absolute()}")
    data, sample_rate = sf.read(str(file))
    sd.play(data, sample_rate)
    sd.wait()
    print("播放结束")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        play_audio(sys.argv[1])
    else:
        print("请提供音频文件路径，例如: python player.py test.wav")
