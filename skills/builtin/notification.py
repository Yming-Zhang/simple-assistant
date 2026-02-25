from typing import Optional, Dict, Any
from skills.base import BaseSkill


class NotificationSkill(BaseSkill):
    """
    系统通知 Skill
    使用 pync 在 macOS 上显示系统通知
    """
    name = "notification"
    description = "显示系统通知"
    keywords = ["通知", "提醒", "提示"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        message = params.get("message", "这是一条通知") if params else "这是一条通知"
        
        try:
            import pync
            pync.notify(message, title="电脑助手")
            return "已发送系统通知"
        except ImportError:
            return "请先安装 pync 库：pip install pync"
        except Exception as e:
            return f"发送通知失败：{str(e)}"
