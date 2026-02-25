from typing import Optional, Tuple, Dict, Any
from .base import BaseMatcher
from skills.base import BaseSkill


class KeywordMatcher(BaseMatcher):
    """
    关键词匹配器
    通过关键词匹配找到对应的 Skill
    """

    def match(self, text: str) -> Tuple[Optional[BaseSkill], Optional[Dict[str, Any]]]:
        """
        匹配文本，找到对应的 Skill
        
        Args:
            text: 输入文本
            
        Returns:
            (skill, params): 匹配到的 Skill 和参数元组
        """
        text_lower = text.lower()
        
        for skill in self.registry.get_all():
            for keyword in skill.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    params = self._extract_params(text, skill)
                    return skill, params
        
        return None, None

    def _extract_params(self, text: str, skill: BaseSkill) -> Optional[Dict[str, Any]]:
        """
        从文本中提取参数
        
        Args:
            text: 输入文本
            skill: 匹配到的 Skill
            
        Returns:
            参数字典（如果没有参数则返回 None）
        """
        params = {}
        
        if skill.name == "hello":
            from typing import List
            greetings: List[str] = ["你好", "hello", "hi"]
            name = self._extract_name(text, greetings)
            if name:
                params["name"] = name
        elif skill.name == "system_cmd":
            cmd = self._extract_cmd(text, skill.keywords)
            if cmd:
                params["cmd"] = cmd
        elif skill.name == "notification":
            message = self._extract_message(text, skill.keywords)
            if message:
                params["message"] = message
        
        return params if params else None

    def _extract_cmd(self, text: str, keywords: list) -> Optional[str]:
        """
        从文本中提取命令/应用名
        
        Args:
            text: 输入文本
            keywords: 关键词列表
            
        Returns:
            命令/应用名（如果没有找到则返回 None）
        """
        for keyword in keywords:
            if keyword in text:
                idx = text.find(keyword)
                remaining = text[idx + len(keyword):].strip()
                if remaining:
                    remaining = remaining.strip(",，！!?。.")
                    if remaining:
                        return remaining
        return None

    def _extract_message(self, text: str, keywords: list) -> Optional[str]:
        """
        从文本中提取通知消息
        
        Args:
            text: 输入文本
            keywords: 关键词列表
            
        Returns:
            通知消息（如果没有找到则返回 None）
        """
        for keyword in keywords:
            if keyword in text:
                idx = text.find(keyword)
                remaining = text[idx + len(keyword):].strip()
                if remaining:
                    remaining = remaining.strip(",，！!?。.")
                    if remaining:
                        return remaining
        return None

    def _extract_name(self, text: str, greetings: list) -> Optional[str]:
        """
        从问候语中提取名字
        
        Args:
            text: 输入文本
            greetings: 问候语列表
            
        Returns:
            名字（如果没有找到则返回 None）
        """
        for greeting in greetings:
            if greeting in text:
                idx = text.find(greeting)
                remaining = text[idx + len(greeting):].strip()
                if remaining:
                    remaining = remaining.strip(",，！!?。.")
                    if remaining:
                        return remaining
        return None
