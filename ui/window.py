import webview
import os
from pathlib import Path


def create_window(bridge_api=None):
    """
    创建 PyWebView 窗口
    """
    current_dir = Path(__file__).parent.parent
    frontend_dist = current_dir / "frontend" / "dist"
    
    html_path = None
    url = None
    
    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        html_path = str(frontend_dist / "index.html")
        print(f"使用生产构建: {html_path}")
    else:
        url = "http://localhost:5173"
        print(f"使用开发服务器: {url}")
    
    window = webview.create_window(
        title="Simple Assistant",
        url=url if url else html_path,
        width=1000,
        height=700,
        resizable=True,
        min_size=(600, 400),
        js_api=bridge_api
    )
    
    return window


if __name__ == "__main__":
    window = create_window()
    webview.start()
