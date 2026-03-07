import subprocess
from typing import Dict, Any, Optional
from skills.base import BaseSkill

class AppControlSkill(BaseSkill):
    """macOS App 控制 Skill"""
    
    name = "app_control"
    description = "控制 macOS 应用（打开、关闭、切换）"
    is_knowledge = False
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        App 控制操作
        
        params: {
            "action": "open|close|activate",  # 操作类型
            "app": "Safari|Chrome|Finder...",  # 应用名称
        }
        """
        if not params:
            params = {}
        
        action = params.get("action", "open")
        app_name = params.get("app", "")
        
        if not app_name:
            return "请指定应用名称"
        
        if action == "open":
            return self._open_app(app_name)
        elif action == "close":
            return self._close_app(app_name)
        elif action == "activate":
            return self._activate_app(app_name)
        else:
            return f"不支持的操作: {action}"
    
    def _open_app(self, app_name: str) -> str:
        """打开应用"""
        try:
            cmd = ["open", "-a", app_name]
            subprocess.run(cmd, check=True)
            return f"已打开应用: {app_name}"
        except Exception as e:
            return f"打开应用失败: {str(e)}"
    
    def _close_app(self, app_name: str) -> str:
        """关闭应用（使用 AppleScript）"""
        try:
            apple_script = f'''
            tell application "{app_name}"
                quit
            end tell
            '''
            cmd = ["osascript", "-e", apple_script]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return f"已关闭应用: {app_name}"
        except Exception as e:
            return f"关闭应用失败: {str(e)}"
    
    def _activate_app(self, app_name: str) -> str:
        """激活/切换到应用"""
        try:
            apple_script = f'''
            tell application "{app_name}"
                activate
            end tell
            '''
            cmd = ["osascript", "-e", apple_script]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return f"已切换到应用: {app_name}"
        except Exception as e:
            return f"切换应用失败: {str(e)}"
