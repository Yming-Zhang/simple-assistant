from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from skills.base import BaseSkill
from skills.registry import SkillRegistry


class BaseMatcher(ABC):
    """
    Matcher 基类
    所有匹配器都必须继承此类并实现 match 方法
    """

    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化 Matcher
        
        Args:
            registry: Skill 注册中心（可选）
        """
        self.registry = registry or SkillRegistry()

    @abstractmethod
    def match(self, text: str) -> Tuple[Optional[BaseSkill], Optional[Dict[str, Any]]]:
        """
        匹配文本，找到对应的 Skill 和参数
        
        Args:
            text: 输入文本
            
        Returns:
            (skill, params): 匹配到的 Skill 和参数元组
        """
        pass

    def set_registry(self, registry: SkillRegistry) -> None:
        """
        设置 Skill 注册中心
        
        Args:
            registry: Skill 注册中心
        """
        self.registry = registry
