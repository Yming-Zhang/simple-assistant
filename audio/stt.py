import os
from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel
from config import config


class STT:
    def __init__(self):
        self.model = None
        self.model_size = config.stt.model_size
        self.model_path = config.stt.model_path
        self.language = config.stt.language
        self.device = config.stt.device

    def _load_model(self):
        if self.model is None:
            if self.model_path:
                print(f"加载本地 Whisper 模型: {self.model_path} (device: {self.device})...")
                self.model = WhisperModel(
                    self.model_path,
                    device=self.device,
                    compute_type="int8"
                )
            else:
                print(f"加载 Whisper 模型: {self.model_size} (device: {self.device})...")
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type="int8"
                )
            print("模型加载完成")

    def transcribe(self, audio_path: str) -> str:
        """
        将音频文件转换为文字
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            识别出的文字
        """
        file = Path(audio_path)
        if not file.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        self._load_model()
        
        print(f"开始识别: {file.absolute()}")
        segments, info = self.model.transcribe(
            str(file),
            language=self.language,
            beam_size=5
        )
        
        text = ""
        for segment in segments:
            text += segment.text.strip() + " "
        
        text = text.strip()
        print(f"识别结果: {text}")
        return text


_stt_instance: Optional[STT] = None


def get_stt() -> STT:
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = STT()
    return _stt_instance


def transcribe(audio_path: str) -> str:
    return get_stt().transcribe(audio_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = transcribe(sys.argv[1])
        print(f"\n最终结果: {result}")
    else:
        print("请提供音频文件路径，例如: python stt.py test.wav")
