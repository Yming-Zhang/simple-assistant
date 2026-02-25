#!/usr/bin/env python3
"""
关键词匹配引擎测试脚本
测试 Matcher 基类和关键词匹配实现
"""

from typing import Dict, Any, Optional
from skills.base import BaseSkill
from skills.registry import get_registry
from matcher.base import BaseMatcher
from matcher.keyword import KeywordMatcher


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
    print("关键词匹配引擎测试")
    print("=" * 50)
    
    registry = get_registry()
    
    print("\n1. 注册 Skills...")
    hello_skill = HelloSkill()
    time_skill = TimeSkill()
    
    registry.register(hello_skill)
    registry.register(time_skill)
    
    print("\n2. 创建关键词匹配器...")
    matcher = KeywordMatcher(registry)
    
    test_cases = [
        "你好",
        "你好，张三",
        "Hello world",
        "Hi，李四",
        "几点了",
        "现在几点了",
        "告诉我时间",
        "这是一句无关的话",
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
