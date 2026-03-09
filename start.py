#!/usr/bin/env python3
"""
Simple Assistant 入口文件
整合：Assistant 主控制器 + PyWebView UI
"""

import logging
import time
import threading
from assistant import Assistant
from ui.bridge import BridgeAPI
from ui.window import create_window
from ui import macos
import webview

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("Simple Assistant - 全能 macOS AI 桌面助手")
    print("=" * 60)
    print()
    
    try:
        # 1. 初始化 Assistant
        assistant = Assistant()
        
        # 2. 初始化 Bridge API，传入 assistant
        bridge = BridgeAPI(assistant=assistant)
        
        # 3. 创建窗口
        window = create_window(bridge_api=bridge)
        bridge.set_window(window)
        
        # 4. 在单独的线程运行唤醒系统，避免阻塞 PyWebView
        def run_wake_system():
            try:
                assistant.wake_system.start(
                    callback=assistant.handle_wakeup,
                    enable_voice=True,
                    enable_key=True
                )
            except Exception as e:
                logger.error(f"唤醒系统启动失败: {e}")
        
        wake_thread = threading.Thread(target=run_wake_system, daemon=True)
        wake_thread.start()
        
        print("✅ 应用启动成功！")
        print("📢 可以使用：")
        print("   - 语音：'Hey Computer' 唤醒")
        print("   - 快捷键：Cmd+Shift+Space 唤醒")
        print("   - UI：在界面直接输入文字或录音")
        print()
        
        # 5. 启动 PyWebView（窗口就绪后定制标题栏）
        def on_started():
            time.sleep(0.5)  # 等待窗口渲染完毕
            macos.customize_titlebar()
        
        webview.start(func=on_started)
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
