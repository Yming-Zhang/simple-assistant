from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from skills.base import BaseSkill


class CameraSkill(BaseSkill):
    """
    摄像头 Skill
    使用 OpenCV 打开摄像头并拍照
    """
    name = "camera"
    description = "打开摄像头并拍照"
    keywords = ["摄像头", "拍照", "打开摄像头", "开启摄像头"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        try:
            import cv2
            
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return "无法打开摄像头"
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return "无法捕获图像"
            
            desktop_path = Path.home() / "Desktop"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            output_path = desktop_path / filename
            
            cv2.imwrite(str(output_path), frame)
            
            return f"拍照成功！已保存到桌面：{filename}"
            
        except ImportError:
            return "请先安装 OpenCV 库：pip install opencv-python"
        except Exception as e:
            return f"摄像头操作失败：{str(e)}"
