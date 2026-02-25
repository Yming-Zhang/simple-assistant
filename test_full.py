#!/usr/bin/env python3
"""
完整功能测试脚本
测试关键词匹配 + 内置 Skills
"""

from typing import Dict, Any, Optional
from skills.base import BaseSkill
from skills.registry import get_registry
from matcher.keyword import KeywordMatcher
from skills.builtin.screen import ScreenSkill
from skills.builtin.camera import CameraSkill
from skills.builtin.system_cmd import SystemCmdSkill
from skills.builtin.notification import NotificationSkill


class HelloSkill(BaseSkill):
    """简单的问候 Skill"""
    name = "hello"
    description = "向用户问好"
    keywords = ["你好", "hello", "hi"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        name = params.get("name", "朋友") if params else "朋友"
        return f"你好，{name}！很高兴见到你！"


class TimeSkill(BaseSkill):
    """获取当前时间的 Skill"""
    name = "time"
    description = "获取当前时间"
    keywords = ["几点", "时间", "现在几点"]

    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        from datetime import datetime
        now = datetime.now()
        return f"现在是 {now.strftime('%H点%M分')}"


def main():
    print("=" * 50)
    print("完整功能测试：关键词匹配 + 内置 Skills")
    print("=" * 50)
    
    registry = get_registry()
    
    print("\n1. 注册所有 Skills...")
    skills = [
        HelloSkill(),
        TimeSkill(),
        ScreenSkill(),
        CameraSkill(),
        SystemCmdSkill(),
        NotificationSkill(),
    ]
    
    for skill in skills:
        registry.register(skill)
        print(f"已注册: {skill.name}")
    
    print(f"\n2. 创建关键词匹配器...")
    matcher = KeywordMatcher(registry)
    
    test_cases = [
        "你好",
        "你好，张三",
        "几点了",
        "截屏",
        "截图",
        "打开 Safari",
        "打开浏览器",
        "通知测试一下",
        "提醒我喝水",
        "摄像头拍照",
    ]
    
    print(f"\n3. 测试 {len(test_cases)} 个用例...\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"测试 {i}: '{text}'")
        skill, params = matcher.match(text)
        
        if skill:
            print(f"  匹配到 Skill: {skill.name}")
            if params:
                print(f"  参数: {params}")
            result = skill.execute(params)
            print(f"  执行结果: {result}")
        else:
            print(f"  未匹配到任何 Skill")
        print()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
