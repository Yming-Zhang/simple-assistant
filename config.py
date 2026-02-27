from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseSettings):
    sample_rate: int = 16000
    channels: int = 1
    record_seconds: int = 5

    model_config = SettingsConfigDict(
        env_prefix="AUDIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class STTConfig(BaseSettings):
    model_size: str = "medium"
    model_path: Optional[str] = None
    language: str = "zh"
    device: str = "auto"

    model_config = SettingsConfigDict(
        env_prefix="STT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class TTSConfig(BaseSettings):
    voice: str = "Meijia"
    rate: float = 1.0

    model_config = SettingsConfigDict(
        env_prefix="TTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class WakeConfig(BaseSettings):
    access_key: Optional[str] = None
    keyword: str = "hey computer"
    hotkey: str = "<cmd>+<shift>+<space>"

    model_config = SettingsConfigDict(
        env_prefix="WAKE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Config(BaseSettings):
    audio: AudioConfig = AudioConfig()
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
    wake: WakeConfig = WakeConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()
