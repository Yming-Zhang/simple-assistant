from skills.base import BaseSkill
from typing import Dict, Any, Optional

class MemorySearchSkill(BaseSkill):
    """记忆搜索 Skill"""
    
    name = "memory_search"
    description = "搜索相关记忆"
    is_knowledge = False
    
    def __init__(self):
        self.conv = None
    
    def set_conversation_manager(self, conversation_manager):
        """设置对话管理器（延迟初始化）"""
        self.conv = conversation_manager
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        搜索记忆
        params: {
            "query": "搜索关键词",
            "days": 3  # 搜索最近几天
        }
        """
        if not self.conv:
            return "记忆系统未初始化"
        
        if not params:
            params = {}
        
        query = params.get("query", "")
        days = params.get("days", 3)
        
        # 简单关键词搜索（后续 Phase X 优化为向量搜索）
        context = self.conv.get_memory_context(include_recent_days=days)
        
        if query:
            # 简单的关键词过滤
            lines = context.split("\n")
            filtered = [line for line in lines if query.lower() in line.lower()]
            if filtered:
                return "找到相关记忆:\n" + "\n".join(filtered)
            else:
                return f"未找到包含 '{query}' 的记忆"
        
        return context

class MemoryGetSkill(BaseSkill):
    """读取具体记忆 Skill"""
    
    name = "memory_get"
    description = "读取具体日期的记忆"
    is_knowledge = False
    
    def __init__(self):
        self.conv = None
    
    def set_conversation_manager(self, conversation_manager):
        """设置对话管理器（延迟初始化）"""
        self.conv = conversation_manager
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        读取记忆
        params: {
            "date": "2026-03-07",  # 可选，默认读取今天
            "type": "day"  # day|long_term
        }
        """
        if not self.conv:
            return "记忆系统未初始化"
        
        if not params:
            params = {}
        
        date_type = params.get("type", "day")
        
        if date_type == "long_term":
            return self.conv.store.get_long_term_memory() or "暂无长期记忆"
        else:
            date_str = params.get("date")
            if date_str:
                return self.conv.store.read_day(date_str) or f"未找到 {date_str} 的记忆"
            else:
                return self.conv.store.read_recent(1) or "暂无近期记忆"
