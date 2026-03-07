from datetime import datetime
from typing import List, Dict, Any
from .store import MemoryStore
from .db import MemoryDB

class ConversationManager:
    """会话管理（滑动窗口 + 记忆注入）"""
    
    def __init__(self, store: MemoryStore, db: MemoryDB, 
                 max_sliding_window: int = 10):
        self.store = store
        self.db = db
        self.max_sliding_window = max_sliding_window
        self.current_session: List[Dict[str, Any]] = []
    
    def add_message(self, role: str, content: str, 
                   timestamp: datetime = None) -> str:
        """添加消息到当前会话并持久化"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 构建消息对象
        msg = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        # 添加到当前会话
        self.current_session.append(msg)
        
        # 限制滑动窗口大小
        if len(self.current_session) > self.max_sliding_window * 2:
            self.current_session = self.current_session[-self.max_sliding_window * 2:]
        
        # 持久化到 Markdown 和 SQLite
        topic = self._extract_topic(content) if role == "user" else None
        
        self.store.append_message(role, content, timestamp)
        self.db.insert_message(timestamp, role, content, topic)
        
        return content
    
    def add_conversation(self, user_msg: str, assistant_msg: str,
                        timestamp: datetime = None):
        """添加一轮对话（用户+助手）"""
        if timestamp is None:
            timestamp = datetime.now()
        
        topic = self._extract_topic(user_msg)
        
        # 添加到当前会话
        self.current_session.append({"role": "user", "content": user_msg, "timestamp": timestamp})
        self.current_session.append({"role": "assistant", "content": assistant_msg, "timestamp": timestamp})
        
        # 限制滑动窗口大小
        if len(self.current_session) > self.max_sliding_window * 2:
            self.current_session = self.current_session[-self.max_sliding_window * 2:]
        
        # 持久化
        self.store.append_conversation(user_msg, assistant_msg, timestamp)
        self.db.insert_conversation(timestamp, user_msg, assistant_msg, topic)
    
    def _extract_topic(self, user_msg: str) -> str:
        """提取简短主题"""
        topic = user_msg[:10]
        if len(user_msg) > 10:
            topic += "..."
        return topic
    
    def get_sliding_window(self) -> List[Dict[str, str]]:
        """获取当前滑动窗口（用于 LLM 上下文）"""
        # 只返回 role 和 content
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.current_session
        ]
    
    def get_memory_context(self, include_long_term: bool = True,
                          include_recent_days: int = 1) -> str:
        """获取记忆上下文（用于注入 LLM prompt）"""
        context_parts = []
        
        # 长期记忆
        if include_long_term:
            long_term = self.store.get_long_term_memory()
            if long_term:
                context_parts.append("## 长期记忆\n" + long_term)
        
        # 最近几天的日志
        if include_recent_days > 0:
            recent = self.store.read_recent(include_recent_days)
            if recent:
                context_parts.append("## 近期对话\n" + recent)
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def build_prompt_with_memory(self, user_input: str,
                                 system_prompt: str = "你是一个有用的助手。") -> str:
        """构建带记忆的完整 prompt"""
        memory_context = self.get_memory_context()
        
        if memory_context:
            full_prompt = f"""{system_prompt}

---

{memory_context}

---

当前对话:
"""
        else:
            full_prompt = system_prompt + "\n\n"
        
        # 添加滑动窗口
        for msg in self.get_sliding_window():
            full_prompt += f"{msg['role']}: {msg['content']}\n"
        
        # 添加当前用户输入
        full_prompt += f"user: {user_input}\n"
        full_prompt += "assistant: "
        
        return full_prompt
    
    def clear_session(self):
        """清空当前会话（不影响持久化记忆）"""
        self.current_session = []
