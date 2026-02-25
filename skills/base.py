from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseSkill(ABC):
    """
    Skill 基类
    所有技能都必须继承此类并实现 execute 方法
    """
    
    name: str
    """技能的唯一名称"""
    
    description: str
    """技能的描述"""
    
    keywords: List[str]
    """用于关键词匹配的关键词列表"""

    @abstractmethod
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        执行技能
        
        Args:
            params: 执行参数（可选）
            
        Returns:
            执行结果消息（将通过 TTS 播放）
        """
        pass

    def __repr__(self) -> str:
        return f"<Skill {self.name}>"
