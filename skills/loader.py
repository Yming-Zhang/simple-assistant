import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type
from skills.base import BaseSkill
from skills.registry import SkillRegistry


class KnowledgeSkill(BaseSkill):
    """知识型 Skill：execute 时返回 prompt 给 LLM"""
    
    def __init__(self, name: str, description: str, prompt: str, keywords: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.prompt_template = prompt
        self.keywords = keywords or []
        self.is_knowledge = True
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """Knowledge Skill 执行时返回提示词"""
        prompt = self.prompt_template
        if params:
            for key, value in params.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt


class SkillLoader:
    """Skill 动态加载器"""
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or SkillRegistry()
        self._loaded_skills: Dict[str, BaseSkill] = {}
    
    def load_from_directory(self, directory: str) -> int:
        """
        从目录加载 Skills
        
        Args:
            directory: 目录路径
            
        Returns:
            加载的 Skill 数量
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return 0
        
        count = 0
        
        # 加载 Python 文件中的 Skills
        for py_file in dir_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            skills = self._load_from_py_file(py_file)
            for skill in skills:
                self.registry.register(skill)
                self._loaded_skills[skill.name] = skill
                count += 1
        
        # 加载 Markdown 文件作为 Knowledge Skills
        for md_file in dir_path.glob("*.md"):
            skill = self._load_from_md_file(md_file)
            if skill:
                self.registry.register(skill)
                self._loaded_skills[skill.name] = skill
                count += 1
        
        return count
    
    def _load_from_py_file(self, file_path: Path) -> List[BaseSkill]:
        """从 Python 文件加载 Skills"""
        skills = []
        spec = importlib.util.spec_from_file_location(f"skill_module_{file_path.stem}", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, BaseSkill) and
                    attr is not BaseSkill and
                    attr is not KnowledgeSkill
                ):
                    try:
                        skill_instance = attr()
                        skills.append(skill_instance)
                    except Exception as e:
                        print(f"警告: 无法实例化 {attr_name}: {e}")
        
        return skills
    
    def _load_from_md_file(self, file_path: Path) -> Optional[KnowledgeSkill]:
        """从 Markdown 文件加载 Knowledge Skill"""
        try:
            content = file_path.read_text(encoding="utf-8")
            name = file_path.stem.replace("_", " ").replace("-", " ")
            
            lines = content.split("\n", 1)
            description = lines[0].strip("# ").strip() if lines else ""
            prompt = lines[1].strip() if len(lines) > 1 else content
            
            return KnowledgeSkill(
                name=name,
                description=description,
                prompt=prompt,
                keywords=[name.lower()]
            )
        except Exception as e:
            print(f"警告: 无法加载 {file_path}: {e}")
            return None
    
    def get_loaded_skills(self) -> Dict[str, BaseSkill]:
        """获取已加载的 Skills"""
        return self._loaded_skills.copy()
