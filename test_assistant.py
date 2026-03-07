#!/usr/bin/env python3
"""
简易测试脚本：快速测试所有 Skills
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from skills.registry import SkillRegistry
from skills.builtin.screen import ScreenSkill
from skills.builtin.camera import CameraSkill
from skills.builtin.system_cmd import SystemCmdSkill
from skills.builtin.notification import NotificationSkill
from skills.builtin.memory import MemorySearchSkill, MemoryGetSkill
from skills.builtin.terminal import TerminalSkill
from skills.builtin.browser import BrowserSkill
from skills.builtin.app_control import AppControlSkill
from skills.builtin.feishu import FeishuSkill

from memory.store import MemoryStore
from memory.db import MemoryDB
from memory.conversation import ConversationManager
from config import config


def test_all_skills():
    """测试所有 Skills"""
    print("=" * 60)
    print("📦 简易测试脚本")
    print("=" * 60)
    
    # 初始化记忆系统
    memory_store = MemoryStore(config.memory.data_dir)
    memory_db = MemoryDB(str(Path(config.memory.data_dir) / "memory.db"))
    conversation_manager = ConversationManager(
        memory_store,
        memory_db,
        max_sliding_window=config.memory.max_sliding_window
    )
    
    # 注册所有 Skills
    registry = SkillRegistry()
    skills = [
        ScreenSkill(),
        CameraSkill(),
        SystemCmdSkill(),
        NotificationSkill(),
        MemorySearchSkill(conversation_manager),
        MemoryGetSkill(conversation_manager),
        TerminalSkill(),
        BrowserSkill(),
        AppControlSkill(),
        FeishuSkill(),
    ]
    
    for skill in skills:
        registry.register(skill)
    
    print(f"\n✅ 已注册 {len(skills)} 个 Skills:")
    for i, skill in enumerate(skills, 1):
        print(f"  {i}. {skill.name}: {skill.description}")
    
    print("\n" + "=" * 60)
    print("🎯 可用的测试指令:")
    print("=" * 60)
    
    commands = [
        ("终端命令", "terminal", {"command": "ls -la"}),
        ("打开浏览器", "browser", {"action": "open", "url": "https://baidu.com"}),
        ("打开应用", "app_control", {"action": "open", "app": "Safari"}),
        ("创建飞书日程", "feishu", {"action": "create_meeting", "title": "测试会议", "time": "2026-03-08 15:00"}),
        ("截屏", "screen", {"action": "capture"}),
        ("发送通知", "notification", {"title": "测试", "content": "这是一条测试通知"}),
    ]
    
    for cmd_name, skill_name, params in commands:
        print(f"\n--- {cmd_name} ---")
        print(f"Skill: {skill_name}")
        print(f"参数: {params}")
        
        # 执行
        try:
            skill = registry.get(skill_name)
            if skill:
                result = skill.execute(params)
                print(f"结果:\n{result}")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_all_skills()
