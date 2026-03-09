from typing import Optional
from pathlib import Path
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
    volume: float = 0.8
    enabled: bool = True
    only_when_wake_by_voice: bool = True

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
    data_dir: str = str(Path(__file__).parent / "data" / "memory")
    conversations_dir: str = "conversations"
    long_term_memory_file: str = "MEMORY.md"
    max_sliding_window: int = 10
    
    model_config = SettingsConfigDict(
        env_prefix="MEMORY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class UIConfig(BaseSettings):
    """UI 动态配置（可通过前端设置面板热更新，持久化在 SQLite settings 表）"""
    theme: str = "blue-gradient"
    default_window_mode: str = "expanded"
    whisper_path: str = ""

    model_config = SettingsConfigDict(
        env_prefix="UI_",
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
    ui: UIConfig = UIConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()


class SettingsManager:
    """
    统一设置管理器：桥接 UI 前端设置 <-> Python config <-> SQLite 持久化
    需要注入 MemoryDB 实例使用
    """
    
    # UI 可热更新的设置键及其默认值
    UI_DEFAULTS = {
        "showThinkingChain": True,
        "model": "qwen3.5",
        "temperature": 0.7,
        "theme": "blue-gradient",
        "voiceReplyEnabled": True,
        "voiceReplyOnlyWhenWakeByVoice": True,
        "voiceReplyVolume": 0.8,
        "whisperPath": "",
        "defaultWindowMode": "expanded",
    }
    
    def __init__(self, db=None):
        self.db = db
    
    def set_db(self, db):
        """注入 MemoryDB"""
        self.db = db
    
    def get_all(self) -> dict:
        """获取所有设置（DB 优先，默认值兜底）"""
        result = dict(self.UI_DEFAULTS)
        if self.db:
            saved = self.db.get_all_settings()
            result.update(saved)
        return result
    
    def update(self, settings: dict):
        """批量更新设置到 DB，并同步到 Python config"""
        if self.db:
            self.db.update_all_settings(settings)
        self._sync_to_config(settings)
    
    def get(self, key: str, default=None):
        """获取单个设置"""
        if self.db:
            val = self.db.get_setting(key)
            if val is not None:
                return val
        return self.UI_DEFAULTS.get(key, default)
    
    def _sync_to_config(self, settings: dict):
        """将前端设置同步到 Python 运行时 config"""
        if "voiceReplyEnabled" in settings:
            config.tts.enabled = bool(settings["voiceReplyEnabled"])
        if "voiceReplyOnlyWhenWakeByVoice" in settings:
            config.tts.only_when_wake_by_voice = bool(settings["voiceReplyOnlyWhenWakeByVoice"])
        if "voiceReplyVolume" in settings:
            config.tts.volume = float(settings["voiceReplyVolume"])
        if "whisperPath" in settings:
            config.ui.whisper_path = str(settings["whisperPath"])
        if "theme" in settings:
            config.ui.theme = str(settings["theme"])
        if "defaultWindowMode" in settings:
            config.ui.default_window_mode = str(settings["defaultWindowMode"])
    
    def validate_whisper_path(self, path: str) -> dict:
        """校验 Whisper 路径是否有效"""
        import os
        if not path:
            return {"valid": False, "message": "路径为空"}
        if not os.path.exists(path):
            return {"valid": False, "message": "路径不存在"}
        if os.path.isfile(path):
            return {"valid": True, "message": "文件存在"}
        if os.path.isdir(path):
            return {"valid": True, "message": "目录存在"}
        return {"valid": False, "message": "未知路径类型"}


# 全局设置管理器单例（DB 在 assistant 初始化时注入）
settings_manager = SettingsManager()
