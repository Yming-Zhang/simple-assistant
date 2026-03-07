import os
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from skills.base import BaseSkill


class ScreenSkill(BaseSkill):
    """
    截屏 Skill（升级：支持 OCR）
    """
    name = "screen"
    description = "截屏并保存到桌面（支持 OCR 文字识别）"
    keywords = ["截屏", "截图", "抓图"]
    is_knowledge = False

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        截屏操作
        
        params: {
            "action": "capture|ocr",  # 操作类型
            "region": null,  # 可选：截图区域 [x, y, width, height]
        }
        """
        if not params:
            params = {}
        
        action = params.get("action", "capture")
        
        if action == "capture":
            return self._capture_screen()
        elif action == "ocr":
            return self._capture_and_ocr()
        else:
            return f"不支持的操作: {action}"
    
    def _capture_screen(self) -> str:
        """截屏并保存"""
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
    
    def _capture_and_ocr(self) -> str:
        """截屏并 OCR 识别（简化版）"""
        # 先截屏
        capture_result = self._capture_screen()
        
        # 简化版 OCR：使用 macOS Vision Framework（通过 Python 调用）
        # 实际项目中可以使用 pyobjc 或 pytesseract
        
        ocr_result = """
OCR 功能说明：
- 完整 OCR 需要：
  1. pyobjc-framework-Vision（macOS Vision API）
  2. 或 pytesseract（跨平台）

当前阶段：仅实现截屏功能
OCR 将在后续 Phase 中完善
"""
        
        return f"{capture_result}\n\n{ocr_result}"
