#!/usr/bin/env python3
"""
Skill 基础架构测试脚本
测试 Skill 基类和注册中心
"""

from typing import Dict, Any, Optional
from skills.base import BaseSkill
from skills.registry import get_registry


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
    print("Skill 基础架构测试")
    print("=" * 50)
    
    registry = get_registry()
    
    print("\n1. 注册 Skills...")
    hello_skill = HelloSkill()
    time_skill = TimeSkill()
    
    registry.register(hello_skill)
    registry.register(time_skill)
    
    print(f"\n已注册的 Skills: {registry.get_names()}")
    
    print("\n2. 测试 HelloSkill...")
    result = hello_skill.execute({"name": "张三"})
    print(f"执行结果: {result}")
    
    print("\n3. 测试 TimeSkill...")
    result = time_skill.execute()
    print(f"执行结果: {result}")
    
    print("\n4. 通过注册中心获取并执行 Skill...")
    skill = registry.get("hello")
    if skill:
        result = skill.execute({"name": "李四"})
        print(f"通过注册中心执行结果: {result}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
