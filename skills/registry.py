from typing import Dict, List, Optional, Type
from skills.base import BaseSkill


class SkillRegistry:
    """Skill 注册中心（增强版）"""
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
    
    def register(self, skill: BaseSkill) -> None:
        """注册一个 Skill"""
        if skill.name in self._skills:
            print(f"警告: Skill '{skill.name}' 已存在，将被覆盖")
        self._skills[skill.name] = skill
        
        # 尝试获取额外元数据信息
        extra_info = ""
        if hasattr(skill, "is_knowledge") and skill.is_knowledge:
            extra_info = " [知识型]"
        print(f"已注册 Skill: {skill.name}{extra_info}")
    
    def get(self, name: str) -> Optional[BaseSkill]:
        """根据名称获取 Skill"""
        return self._skills.get(name)
    
    def get_all(self) -> List[BaseSkill]:
        """获取所有注册的 Skill"""
        return list(self._skills.values())
    
    def get_names(self) -> List[str]:
        """获取所有注册的 Skill 名称"""
        return list(self._skills.keys())
    
    def unregister(self, name: str) -> bool:
        """注销一个 Skill"""
        if name in self._skills:
            del self._skills[name]
            print(f"已注销 Skill: {name}")
            return True
        return False
    
    def clear(self) -> None:
        """注销所有 Skill"""
        self._skills.clear()
        print("已清空所有 Skill")


_registry_instance: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """获取全局 Skill 注册中心实例"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SkillRegistry()
    return _registry_instance
