#!/usr/bin/env python3
"""
启动脚本
用于启动电脑助手
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from assistant import main


def check_venv():
    """
    检查是否在虚拟环境中运行
    """
    if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
        print("警告: 未在虚拟环境中运行，可能会遇到依赖问题")
        print("建议: 先执行 source venv/bin/activate")
        print("按 Enter 继续，或按 Ctrl+C 退出")
        input()


def check_dependencies():
    """
    检查关键依赖是否安装
    """
    try:
        import sounddevice
        import faster_whisper
        import edge_tts
        import pynput
        import mss
        import pync
        print("✅ 所有关键依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请执行: pip install -e .")
        sys.exit(1)


def print_welcome():
    """
    打印欢迎信息
    """
    print("=" * 60)
    print("🎤 电脑助手启动脚本")
    print("=" * 60)
    print("\n功能介绍:")
    print("- 语音唤醒: 说 'hey computer'")
    print("- 按键唤醒: 按 Cmd+Shift+Space")
    print("- 支持的命令:")
    print("  • 截屏/截图/抓图")
    print("  • 摄像头/拍照")
    print("  • 打开 Safari/Chrome/Terminal/Finder")
    print("  • 通知/提醒/提示")
    print("  • 几点/时间/现在几点")
    print("  • 你好/hello/hi")
    print("\n按 Ctrl+C 退出")
    print("=" * 60)


def main():
    """
    主函数
    """
    try:
        print_welcome()
        check_venv()
        check_dependencies()
        
        print("\n启动电脑助手...")
        from assistant import main as assistant_main
        assistant_main()
        
    except KeyboardInterrupt:
        print("\n正在退出...")
    except Exception as e:
        print(f"\n启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
