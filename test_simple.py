#!/usr/bin/env python3
"""
超简易测试脚本：只测试核心 Skills，不依赖配置
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from skills.builtin.screen import ScreenSkill
from skills.builtin.terminal import TerminalSkill
from skills.builtin.browser import BrowserSkill
from skills.builtin.app_control import AppControlSkill
from skills.builtin.feishu import FeishuSkill
from skills.builtin.notification import NotificationSkill


def test_simple():
    """简易测试"""
    print("=" * 60)
    print("🧪 超简易测试脚本")
    print("=" * 60)
    
    print("\n✅ 已加载的 Skills:")
    skills = [
        ("screen", ScreenSkill()),
        ("terminal", TerminalSkill()),
        ("browser", BrowserSkill()),
        ("app_control", AppControlSkill()),
        ("feishu", FeishuSkill()),
        ("notification", NotificationSkill()),
    ]
    
    for name, skill in skills:
        print(f"  - {name}: {skill.description}")
    
    print("\n" + "=" * 60)
    print("🎯 开始测试:")
    print("=" * 60)
    
    # 1. 测试 terminal
    print("\n--- 1. 测试 terminal (ls -la) ---")
    try:
        result = TerminalSkill().execute({"command": "ls -la"})
        print(result[:300] + "..." if len(result) > 300 else result)
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 2. 测试 notification
    print("\n--- 2. 测试 notification ---")
    try:
        result = NotificationSkill().execute({"title": "测试通知", "content": "Phase 11 & 12 完成！"})
        print(result)
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 3. 测试 feishu
    print("\n--- 3. 测试 feishu ---")
    try:
        result = FeishuSkill().execute({
            "action": "create_meeting",
            "title": "Phase 验收会议",
            "time": "2026-03-08 15:00"
        })
        print(result)
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 简易测试完成！")
    print("\n📝 你可以尝试的完整指令（启动服务后）:")
    print("  1. 帮我执行 ls -la")
    print("  2. 打开浏览器，访问 baidu.com")
    print("  3. 打开 Safari")
    print("  4. 创建一个飞书日程，明天下午3点")
    print("  5. 截屏")
    print("  6. 发送一条通知：hello")
    print("=" * 60)


if __name__ == "__main__":
    test_simple()
