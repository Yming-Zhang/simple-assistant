import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from config import config


def record_audio(output_path: str = "output.wav", seconds: int = None) -> str:
    """
    录音并保存为 WAV 文件
    
    Args:
        output_path: 输出文件路径
        seconds: 录音时长（秒），如果为 None 则使用配置中的时长
    
    Returns:
        输出文件路径
    """
    if seconds is None:
        seconds = config.audio.record_seconds
    
    sample_rate = config.audio.sample_rate
    channels = config.audio.channels
    
    print(f"开始录音，时长 {seconds} 秒...")
    recording = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype="float32"
    )
    sd.wait()
    print("录音结束")
    
    output_file = Path(output_path)
    sf.write(str(output_file), recording, sample_rate)
    print(f"音频已保存到: {output_file.absolute()}")
    
    return str(output_file)


if __name__ == "__main__":
    record_audio("test_recording.wav")
