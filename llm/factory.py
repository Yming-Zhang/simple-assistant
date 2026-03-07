from typing import Optional, Dict, Any
from .base import LLMProvider
from .ollama import OllamaProvider
from .azure_openai import AzureOpenAIProvider


class LLMProviderFactory:
    """LLM Provider 工厂"""
    
    @staticmethod
    def create(
        provider_type: str,
        config: Dict[str, Any]
    ) -> LLMProvider:
        """
        创建 LLM Provider 实例
        
        Args:
            provider_type: "ollama" 或 "azure_openai"
            config: 配置字典
            
        Returns:
            LLMProvider 实例
        """
        provider_type = provider_type.lower()
        
        if provider_type == "ollama":
            return OllamaProvider(
                base_url=config.get("base_url", "http://localhost:11434"),
                model=config.get("model", "qwen3.5:4b"),
                timeout=config.get("timeout", 120)
            )
        
        elif provider_type == "azure_openai":
            required_fields = ["endpoint", "api_key", "deployment_name"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Azure OpenAI 配置缺少必需字段: {field}")
            
            return AzureOpenAIProvider(
                endpoint=config["endpoint"],
                api_key=config["api_key"],
                deployment_name=config["deployment_name"],
                api_version=config.get("api_version", "2024-02-15-preview"),
                timeout=config.get("timeout", 120)
            )
        
        else:
            raise ValueError(f"不支持的 provider 类型: {provider_type}")
