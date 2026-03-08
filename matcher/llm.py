import json
import asyncio
from typing import Optional, Tuple, Dict, Any
from .base import BaseMatcher
from skills.base import BaseSkill
from skills.registry import SkillRegistry
from llm.base import LLMProvider
from llm.response import ChatResponse
from llm.factory import LLMProviderFactory
from config import config


class LLMMatcher(BaseMatcher):
    """LLM 驱动的匹配器"""
    
    def __init__(self, registry: Optional[SkillRegistry] = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        super().__init__(registry)
        self.provider: Optional[LLMProvider] = None
        self.loop = loop or asyncio.new_event_loop()
        self._init_provider()
        self.last_reasoning: Optional[str] = None
    
    def _init_provider(self):
        """初始化 LLM Provider"""
        try:
            self.provider = LLMProviderFactory.create(
                config.llm.provider,
                config.llm.get_provider_config()
            )
        except Exception as e:
            print(f"警告: 初始化 LLM Provider 失败: {e}")
            print("将回退到关键词匹配")
    
    def _build_skills_description(self) -> str:
        """构建技能描述"""
        skills = self.registry.get_all()
        descriptions = []
        for skill in skills:
            desc = f"- {skill.name}: {skill.description}"
            if hasattr(skill, "keywords") and skill.keywords:
                desc += f" (关键词: {', '.join(skill.keywords)})"
            if hasattr(skill, "is_knowledge") and skill.is_knowledge:
                desc += " [知识型]"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""你是一个智能助手，负责分析用户的请求并匹配到合适的技能。

可用的技能列表：
{self._build_skills_description()}

请按照以下 JSON 格式输出结果：
{{
    "skill_name": "匹配到的技能名称，如果没有匹配则为 null",
    "params": {{
        "参数名": "参数值"
    }},
    "confidence": 0.0-1.0 的置信度分数,
    "reasoning": "简短的推理说明"
}}

要求：
1. 只返回 JSON，不要有其他文字
2. 如果用户请求不匹配任何技能，skill_name 返回 null
3. params 根据技能需要提取，没有参数则返回空对象 {{}}
"""
    
    def _parse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception:
            pass
        return None
    
    def match(self, text: str) -> Tuple[Optional[BaseSkill], Optional[Dict[str, Any]]]:
        """
        匹配文本，找到对应的 Skill 和参数
        
        Args:
            text: 输入文本
            
        Returns:
            (skill, params): 匹配到的 Skill 和参数元组
        """
        self.last_reasoning = None
        
        if self.provider is None:
            print("LLM Provider 未初始化，回退到关键词匹配")
            from .keyword import KeywordMatcher
            return KeywordMatcher(self.registry).match(text)
        
        try:
            # 同步运行异步调用
            result = self.loop.run_until_complete(self._async_match(text))
            return result
        except Exception as e:
            print(f"LLM 匹配出错: {e}")
            import traceback
            print(traceback.format_exc())
            print("回退到关键词匹配")
            from .keyword import KeywordMatcher
            return KeywordMatcher(self.registry).match(text)
    
    async def _async_match(self, text: str) -> Tuple[Optional[BaseSkill], Optional[Dict[str, Any]]]:
        """异步匹配"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": text}
        ]
        
        response: ChatResponse = await self.provider.chat(
            messages,
            include_reasoning=True
        )
        
        self.last_reasoning = response.reasoning
        
        parsed = self._parse_response(response.content)
        
        if parsed and parsed.get("skill_name"):
            skill = self.registry.get(parsed["skill_name"])
            if skill:
                print(f"LLM 匹配到: {skill.name} (置信度: {parsed.get('confidence', 0)})")
                if self.last_reasoning:
                    print(f"推理: {self.last_reasoning}")
                return skill, parsed.get("params", {})
        
        return None, None
    
    def get_last_reasoning(self) -> Optional[str]:
        """获取最后一次的 reasoning（推导链）"""
        return self.last_reasoning
    
    async def stream_match(self, text: str, on_chunk):
        """
        流式匹配文本，找到对应的 Skill 和参数
        
        Args:
            text: 输入文本
            on_chunk: 回调函数，接收 (type, content)，type 可以是 'reasoning' 或 'content'
            
        Returns:
            (skill, params): 匹配到的 Skill 和参数元组
        """
        self.last_reasoning = None
        
        if self.provider is None:
            print("LLM Provider 未初始化，回退到关键词匹配")
            from .keyword import KeywordMatcher
            return KeywordMatcher(self.registry).match(text)
        
        try:
            messages = [
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": text}
            ]
            
            full_reasoning = ""
            full_content = ""
            
            async for chunk in self.provider.stream_chat(messages, include_reasoning=True):
                if chunk.reasoning:
                    full_reasoning += chunk.reasoning
                    await on_chunk("reasoning", full_reasoning)
                
                if chunk.content:
                    full_content += chunk.content
                
                if chunk.is_finished:
                    break
            
            self.last_reasoning = full_reasoning
            
            parsed = self._parse_response(full_content)
            
            if parsed and parsed.get("skill_name"):
                skill = self.registry.get(parsed["skill_name"])
                if skill:
                    print(f"LLM 匹配到: {skill.name} (置信度: {parsed.get('confidence', 0)})")
                    if self.last_reasoning:
                        print(f"推理: {self.last_reasoning}")
                    return skill, parsed.get("params", {})
            
            return None, None
            
        except Exception as e:
            print(f"LLM 匹配出错: {e}")
            import traceback
            print(traceback.format_exc())
            print("回退到关键词匹配")
            from .keyword import KeywordMatcher
            return KeywordMatcher(self.registry).match(text)
