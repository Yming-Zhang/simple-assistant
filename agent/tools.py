from typing import List, Dict, Any, Optional
from skills.base import BaseSkill
from skills.registry import SkillRegistry

class ToolConverter:
    """Skills → LLM Function Calling 格式转换"""
    
    @staticmethod
    def skill_to_function(skill: BaseSkill) -> Dict[str, Any]:
        """将单个 Skill 转换为 LLM function calling 格式"""
        
        # 构建 parameters schema（简化版，后续可扩展）
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # 从 Skill 的 execute 参数推断（简化实现）
        # 实际项目中可以使用类型注解或 pydantic 模型
        if hasattr(skill, 'params_schema'):
            parameters = skill.params_schema
        
        return {
            "type": "function",
            "function": {
                "name": skill.name,
                "description": skill.description,
                "parameters": parameters
            }
        }
    
    @staticmethod
    def registry_to_functions(registry: SkillRegistry) -> List[Dict[str, Any]]:
        """将整个 SkillRegistry 转换为 function list"""
        functions = []
        for skill in registry.get_all():
            functions.append(ToolConverter.skill_to_function(skill))
        return functions
    
    @staticmethod
    def parse_tool_call(tool_call: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """解析 LLM 返回的 tool_call"""
        # 兼容 Ollama 和 Azure OpenAI 的格式
        if "function" in tool_call:
            # Ollama 格式
            func = tool_call["function"]
            name = func.get("name", "")
            arguments = func.get("arguments", {})
        else:
            # Azure OpenAI 格式
            name = tool_call.get("name", "")
            arguments = tool_call.get("arguments", {})
        
        # 如果 arguments 是字符串，尝试解析为 JSON
        if isinstance(arguments, str):
            import json
            try:
                arguments = json.loads(arguments)
            except:
                arguments = {}
        
        return name, arguments
