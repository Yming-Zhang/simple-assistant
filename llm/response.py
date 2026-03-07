from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, AsyncIterator


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    reasoning: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamChunk:
    """流式响应块"""
    content: str = ""
    reasoning: str = ""
    is_finished: bool = False
