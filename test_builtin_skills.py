#!/usr/bin/env python3
"""
内置 Skills 测试脚本
测试截屏、摄像头、系统命令、通知等功能
"""

from skills.registry import get_registry
from skills.builtin.screen import ScreenSkill
from skills.builtin.camera import CameraSkill
from skills.builtin.system_cmd import SystemCmdSkill
from skills.builtin.notification import NotificationSkill


def main():
    print("=" * 50)
    print("内置 Skills 测试")
    print("=" * 50)
    
    registry = get_registry()
    
    print("\n1. 注册 Skills...")
    skills = [
        ScreenSkill(),
        CameraSkill(),
        SystemCmdSkill(),
        NotificationSkill(),
    ]
    
    for skill in skills:
        registry.register(skill)
        print(f"已注册: {skill.name} - {skill.description}")
    
    print(f"\n2. 显示所有已注册 Skills:")
    for skill in registry.get_all():
        print(f"- {skill.name}: {skill.keywords}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
