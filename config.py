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


class LLMConfig(BaseSettings):
    """LLM 配置"""
    provider: str = "ollama"  # "ollama" 或 "azure_openai"
    
    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:4b"
    ollama_timeout: int = 120
    
    # Azure OpenAI 配置
    azure_endpoint: Optional[str] = None
    azure_api_key: Optional[str] = None
    azure_deployment_name: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"
    azure_timeout: int = 120
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    def get_provider_config(self) -> dict:
        """获取当前 provider 的配置字典"""
        if self.provider == "ollama":
            return {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
                "timeout": self.ollama_timeout
            }
        elif self.provider == "azure_openai":
            return {
                "endpoint": self.azure_endpoint,
                "api_key": self.azure_api_key,
                "deployment_name": self.azure_deployment_name,
                "api_version": self.azure_api_version,
                "timeout": self.azure_timeout
            }
        else:
            raise ValueError(f"不支持的 provider: {self.provider}")


class MemoryConfig(BaseSettings):
    """记忆系统配置"""
    data_dir: str = "./data/memory"
    conversations_dir: str = "conversations"
    long_term_memory_file: str = "MEMORY.md"
    max_sliding_window: int = 10
    
    model_config = SettingsConfigDict(
        env_prefix="MEMORY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Config(BaseSettings):
    audio: AudioConfig = AudioConfig()
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
    wake: WakeConfig = WakeConfig()
    llm: LLMConfig = LLMConfig()
    memory: MemoryConfig = MemoryConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()
