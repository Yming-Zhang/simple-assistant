import subprocess
import shlex
from typing import Optional, Dict, Any
from skills.base import BaseSkill


class SystemCmdSkill(BaseSkill):
    """
    系统命令 Skill
    用于执行系统命令，如打开应用等
    """
    name = "system_cmd"
    description = "执行系统命令或打开应用"
    keywords = ["打开", "启动", "运行", "执行"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        if not params or "cmd" not in params:
            return "请指定要执行的命令或打开的应用"
        
        cmd = params["cmd"]
        
        try:
            if cmd.lower() in ["safari", "浏览器", "Safari"]:
                subprocess.run(["open", "-a", "Safari"], check=True)
                return "已打开 Safari 浏览器"
            elif cmd.lower() in ["chrome", "谷歌", "Chrome"]:
                subprocess.run(["open", "-a", "Google Chrome"], check=True)
                return "已打开 Chrome 浏览器"
            elif cmd.lower() in ["terminal", "终端", "Terminal"]:
                subprocess.run(["open", "-a", "Terminal"], check=True)
                return "已打开终端"
            elif cmd.lower() in ["finder", "访达", "Finder"]:
                subprocess.run(["open", "-a", "Finder"], check=True)
                return "已打开 Finder"
            else:
                subprocess.run(["open", "-a", cmd], check=True)
                return f"已打开 {cmd}"
                
        except subprocess.CalledProcessError:
            return f"无法打开应用：{cmd}"
        except Exception as e:
            return f"执行命令失败：{str(e)}"
