import subprocess
import shlex
from typing import Dict, Any, Optional
from skills.base import BaseSkill

class TerminalSkill(BaseSkill):
    """终端命令执行 Skill"""
    
    name = "terminal"
    description = "执行终端命令"
    is_knowledge = False
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        执行终端命令
        
        params: {
            "command": "ls -la",  # 要执行的命令
            "timeout": 30         # 超时时间（秒）
        }
        """
        if not params:
            params = {}
        
        command = params.get("command", "")
        timeout = params.get("timeout", 30)
        
        if not command:
            return "请指定要执行的命令"
        
        try:
            # 安全地解析命令
            args = shlex.split(command)
            
            # 执行命令
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = []
            if result.stdout:
                output.append(f"标准输出:\n{result.stdout}")
            if result.stderr:
                output.append(f"标准错误:\n{result.stderr}")
            output.append(f"退出码: {result.returncode}")
            
            return "\n".join(output)
            
        except subprocess.TimeoutExpired:
            return f"命令执行超时（{timeout}秒）"
        except Exception as e:
            return f"命令执行失败: {str(e)}"
