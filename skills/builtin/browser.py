import webbrowser
import subprocess
from typing import Dict, Any, Optional
from skills.base import BaseSkill

class BrowserSkill(BaseSkill):
    """浏览器自动化 Skill"""
    
    name = "browser"
    description = "浏览器自动化操作（打开、导航）"
    is_knowledge = False
    
    # 常见浏览器 bundle ID
    BROWSERS = {
        "chrome": "com.google.Chrome",
        "safari": "com.apple.Safari",
        "firefox": "org.mozilla.firefox",
        "edge": "com.microsoft.edgemac"
    }
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        浏览器操作
        
        params: {
            "action": "open|navigate",  # 操作类型
            "url": "https://example.com",  # 要打开的 URL
            "browser": "chrome",  # 浏览器类型（可选）
        }
        """
        if not params:
            params = {}
        
        action = params.get("action", "open")
        url = params.get("url", "")
        browser = params.get("browser", "default")
        
        if action == "open":
            return self._open_browser(url, browser)
        elif action == "navigate":
            return self._navigate(url, browser)
        else:
            return f"不支持的操作: {action}"
    
    def _open_browser(self, url: str, browser: str) -> str:
        """打开浏览器"""
        try:
            if browser == "default" or browser not in self.BROWSERS:
                if url:
                    webbrowser.open(url)
                    return f"已在默认浏览器打开: {url}"
                else:
                    webbrowser.open("https://www.google.com")
                    return "已打开默认浏览器"
            else:
                # 使用 macOS open 命令打开指定浏览器
                bundle_id = self.BROWSERS[browser]
                if url:
                    cmd = ["open", "-a", bundle_id, url]
                else:
                    cmd = ["open", "-a", bundle_id]
                
                subprocess.run(cmd, check=True)
                display_url = url if url else "(新标签页)"
                return f"已在 {browser} 打开: {display_url}"
                
        except Exception as e:
            return f"打开浏览器失败: {str(e)}"
    
    def _navigate(self, url: str, browser: str) -> str:
        """导航到 URL（简化版，同 open）"""
        if not url:
            return "请指定要导航的 URL"
        return self._open_browser(url, browser)
