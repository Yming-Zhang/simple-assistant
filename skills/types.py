from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    keywords: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_knowledge: bool = False  # 可选：是否是知识型 Skill
    category: Optional[str] = None  # 可选：分类标签
