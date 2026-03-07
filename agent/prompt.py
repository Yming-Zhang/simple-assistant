from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """Prompt 模板"""
    name: str
    template: str
    description: str = ""

class PromptManager:
    """System Prompt 模板管理"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._init_default_templates()
    
    def _init_default_templates(self):
        """初始化默认模板"""
        
        # 基础助手模板
        self.templates["default"] = PromptTemplate(
            name="default",
            description="默认助手模板",
            template="""你是一个有用的电脑助手。你可以帮助用户完成各种任务。

你可以使用工具来帮助用户。当你需要使用工具时，请调用相应的函数。

回答要求：
- 用简洁的中文回答
- 如果需要使用工具，先调用工具，再根据结果回答
- 如果不需要工具，直接回答用户的问题"""
        )
        
        # 电脑操作专家模板
        self.templates["computer_expert"] = PromptTemplate(
            name="computer_expert",
            description="电脑操作专家模板",
            template="""你是一个专业的电脑操作专家。你精通 macOS 系统操作，可以帮助用户完成各种电脑自动化任务。

你可以使用以下类型的工具：
- 终端命令执行
- 浏览器自动化
- App 控制
- 截屏和 OCR
- 日程管理

工作流程：
1. 理解用户需求
2. 选择合适的工具
3. 调用工具执行
4. 根据结果继续或完成

回答要求：
- 专业、准确
- 清晰说明正在执行的操作
- 如果需要多个步骤，逐步执行"""
        )
        
        # 带记忆的助手模板
        self.templates["with_memory"] = PromptTemplate(
            name="with_memory",
            description="带记忆的助手模板",
            template="""你是一个有用的电脑助手。你可以帮助用户完成各种任务。

你可以使用工具来帮助用户。当你需要使用工具时，请调用相应的函数。

{memory_context}

回答要求：
- 用简洁的中文回答
- 如果需要使用工具，先调用工具，再根据结果回答
- 如果不需要工具，直接回答用户的问题
- 参考历史记忆来更好地理解用户需求"""
        )
    
    def get_template(self, name: str) -> Optional[str]:
        """获取模板"""
        if name in self.templates:
            return self.templates[name].template
        return None
    
    def render(self, name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.get_template(name)
        if template:
            return template.format(**kwargs)
        return ""
    
    def add_template(self, name: str, template: str, description: str = ""):
        """添加自定义模板"""
        self.templates[name] = PromptTemplate(
            name=name,
            template=template,
            description=description
        )
