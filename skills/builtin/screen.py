from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from skills.base import BaseSkill


class ScreenSkill(BaseSkill):
    """
    截屏 Skill
    使用 mss 库进行高性能截屏
    """
    name = "screen"
    description = "截屏并保存到桌面"
    keywords = ["截屏", "截图", "抓图"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        try:
            import mss
            from PIL import Image
            
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
                desktop_path = Path.home() / "Desktop"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                output_path = desktop_path / filename
                
                img.save(output_path)
                
                return f"截屏成功！已保存到桌面：{filename}"
                
        except ImportError:
            return "请先安装 mss 和 Pillow 库：pip install mss Pillow"
        except Exception as e:
            return f"截屏失败：{str(e)}"
