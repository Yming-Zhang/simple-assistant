from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskStep:
    """任务步骤"""
    step_num: int
    description: str
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None

class TaskPlanner:
    """多步骤任务编排"""
    
    def __init__(self):
        self.steps: List[TaskStep] = []
    
    def parse_plan(self, plan_text: str) -> List[TaskStep]:
        """从文本解析任务计划"""
        # 简化实现：按行解析
        lines = plan_text.strip().split("\n")
        steps = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                # 尝试提取工具调用
                tool_name = None
                tool_params = None
                
                # 简单模式匹配
                if "->" in line:
                    parts = line.split("->")
                    description = parts[0].strip()
                    tool_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    if "(" in tool_part and ")" in tool_part:
                        import re
                        match = re.match(r"(\w+)\((.*)\)", tool_part)
                        if match:
                            tool_name = match.group(1)
                            params_str = match.group(2)
                            # 简单解析参数
                            tool_params = {}
                            if params_str:
                                for param in params_str.split(","):
                                    param = param.strip()
                                    if "=" in param:
                                        key, value = param.split("=", 1)
                                        tool_params[key.strip()] = value.strip().strip("\"'")
                else:
                    description = line
                
                steps.append(TaskStep(
                    step_num=i + 1,
                    description=description,
                    tool_name=tool_name,
                    tool_params=tool_params
                ))
        
        self.steps = steps
        return steps
    
    def get_next_step(self) -> Optional[TaskStep]:
        """获取下一个待执行的步骤"""
        for step in self.steps:
            if step.status == TaskStatus.PENDING:
                return step
        return None
    
    def update_step(self, step_num: int, status: TaskStatus, 
                   result: Optional[str] = None):
        """更新步骤状态"""
        for step in self.steps:
            if step.step_num == step_num:
                step.status = status
                if result is not None:
                    step.result = result
                break
    
    def get_plan_summary(self) -> str:
        """获取计划摘要"""
        summary = []
        for step in self.steps:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌"
            }.get(step.status, "?")
            
            summary.append(f"{status_icon} Step {step.step_num}: {step.description}")
            if step.result:
                summary.append(f"   结果: {step.result}")
        
        return "\n".join(summary)
    
    def is_complete(self) -> bool:
        """检查计划是否完成"""
        return all(
            step.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            for step in self.steps
        )
