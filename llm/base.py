from abc import ABC, abstractmethod
from typing import AsyncIterator, Any, Optional
from .response import ChatResponse, StreamChunk


class LLMProvider(ABC):
    """LLM 提供者抽象基类"""
    
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        include_reasoning: bool = True,
        **kwargs
    ) -> ChatResponse:
        """
        同步调用 LLM，返回完整响应
        
        Args:
            messages: 消息列表，OpenAI 格式
            tools: 工具定义列表（可选）
            include_reasoning: 是否包含推导链
            **kwargs: 其他参数
            
        Returns:
            ChatResponse 对象
        """
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict],
        include_reasoning: bool = True,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        流式调用 LLM，逐 token 返回
        
        Args:
            messages: 消息列表，OpenAI 格式
            include_reasoning: 是否包含推导链
            **kwargs: 其他参数
            
        Yields:
            StreamChunk 对象
        """
        pass
