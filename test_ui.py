#!/usr/bin/env python3
"""
测试 UI（Phase 14 & 15）
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ui.window import create_window
    HAS_WEBVIEW = True
except ImportError:
    create_window = None
    HAS_WEBVIEW = False

from ui.bridge import BridgeAPI


def test_bridge_api():
    """测试 BridgeAPI 初始化"""
    print("=" * 50)
    print("测试 BridgeAPI 初始化")
    print("=" * 50)
    
    bridge = BridgeAPI(None)
    
    print("\n✅ BridgeAPI 初始化成功")
    print("\n可用方法:")
    for attr in dir(bridge):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    print("\n✅ 测试 BridgeAPI.send_message()")
    bridge.send_message("你好")
    
    print("\n✅ 测试多模态消息（图片）")
    bridge.send_message("这是什么图片?", ["data:image/png;base64,test"])
    
    print("\n✅ 所有测试通过！")
    return True


def main():
    """主函数 - 启动完整应用"""
    print("=" * 50)
    print("Simple Assistant - UI 测试")
    print("=" * 50)
    
    if not HAS_WEBVIEW:
        print("\n⚠️  pywebview 未安装，仅运行 BridgeAPI 测试")
        test_bridge_api()
        return
    
    print("\n1. 初始化 BridgeAPI...")
    bridge = BridgeAPI(None)
    
    print("2. 创建 PyWebView 窗口...")
    window = create_window(bridge)
    bridge.set_window(window)
    
    print("3. 启动应用...")
    import webview
    webview.start()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = test_bridge_api()
        sys.exit(0 if success else 1)
    else:
        main()
