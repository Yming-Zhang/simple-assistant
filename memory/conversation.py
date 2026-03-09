from datetime import datetime
from typing import List, Dict, Any, Optional
from .store import MemoryStore
from .db import MemoryDB

class ConversationManager:
    """会话管理（支持多会话 + 滑动窗口 + 记忆注入）"""
    
    def __init__(self, store: MemoryStore, db: MemoryDB, 
                 max_sliding_window: int = 10):
        self.store = store
        self.db = db
        self.max_sliding_window = max_sliding_window
        self.current_session: List[Dict[str, Any]] = []
        self._current_conversation_id: Optional[str] = None
    
    # ---- 会话级 CRUD ----
    
    @property
    def current_conversation_id(self) -> Optional[str]:
        return self._current_conversation_id
    
    def ensure_conversation(self) -> str:
        """确保有一个当前会话，没有则自动创建"""
        if not self._current_conversation_id:
            self._current_conversation_id = self.create_conversation()
        return self._current_conversation_id
    
    def set_current_conversation(self, conv_id: str):
        """切换当前会话，加载其消息到 session"""
        self._current_conversation_id = conv_id
        # 从 DB 加载消息到 sliding window
        messages = self.db.get_conversation_messages(conv_id)
        self.current_session = []
        for msg in messages:
            self.current_session.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp", ""),
                "images": msg.get("images", [])
            })
        # 限制滑动窗口
        if len(self.current_session) > self.max_sliding_window * 2:
            self.current_session = self.current_session[-self.max_sliding_window * 2:]
    
    def create_conversation(self, title: str = "新对话") -> str:
        """创建新会话，返回 conversation_id"""
        conv_id = self.db.create_conversation(title)
        self._current_conversation_id = conv_id
        self.current_session = []
        return conv_id
    
    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """列出所有会话摘要"""
        return self.db.list_conversations(limit)
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """获取指定会话的完整信息（包含消息列表）"""
        conv = self.db.get_conversation(conv_id)
        if not conv:
            return None
        messages = self.db.get_conversation_messages(conv_id)
        conv["messages"] = messages
        return conv
    
    def rename_conversation(self, conv_id: str, title: str) -> bool:
        """重命名会话"""
        return self.db.rename_conversation(conv_id, title)
    
    def delete_conversation(self, conv_id: str) -> bool:
        """删除会话"""
        success = self.db.delete_conversation(conv_id)
        if success and self._current_conversation_id == conv_id:
            self._current_conversation_id = None
            self.current_session = []
        return success

    def resume_last_conversation(self) -> Optional[str]:
        """恢复最近一次会话（启动时调用），返回 conversation_id 或 None"""
        convs = self.list_conversations(limit=1)
        if convs:
            last_id = convs[0]["id"]
            self.set_current_conversation(last_id)
            return last_id
        return None
    
    # ---- 消息操作 ----
    
    def add_message(self, role: str, content: str, 
                   timestamp: datetime = None,
                   images: Optional[List[str]] = None) -> str:
        """添加消息到当前会话并持久化"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 确保有当前会话
        conv_id = self.ensure_conversation()
        
        # 构建消息对象
        msg = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "images": images or []
        }
        
        # 添加到当前会话
        self.current_session.append(msg)
        
        # 限制滑动窗口大小
        if len(self.current_session) > self.max_sliding_window * 2:
            self.current_session = self.current_session[-self.max_sliding_window * 2:]
        
        # 提取主题（用于自动命名会话）
        topic = self._extract_topic(content) if role == "user" else None
        
        # 如果是第一条用户消息，自动给会话起名
        if role == "user" and topic:
            conv = self.db.get_conversation(conv_id)
            if conv and conv.get("title") == "新对话":
                auto_title = content[:20] + ("..." if len(content) > 20 else "")
                self.db.rename_conversation(conv_id, auto_title)
        
        # 持久化到 Markdown 和 SQLite
        self.store.append_message(role, content, timestamp)
        self.db.insert_message(timestamp, role, content, topic, conv_id, images)
        
        return content
    
    def add_conversation(self, user_msg: str, assistant_msg: str,
                        timestamp: datetime = None):
        """添加一轮对话（用户+助手）"""
        if timestamp is None:
            timestamp = datetime.now()
        
        conv_id = self.ensure_conversation()
        topic = self._extract_topic(user_msg)
        
        # 添加到当前会话
        self.current_session.append({"role": "user", "content": user_msg, "timestamp": timestamp})
        self.current_session.append({"role": "assistant", "content": assistant_msg, "timestamp": timestamp})
        
        # 限制滑动窗口大小
        if len(self.current_session) > self.max_sliding_window * 2:
            self.current_session = self.current_session[-self.max_sliding_window * 2:]
        
        # 持久化
        self.store.append_conversation(user_msg, assistant_msg, timestamp)
        self.db.insert_conversation(timestamp, user_msg, assistant_msg, topic, conv_id)
    
    def _extract_topic(self, user_msg: str) -> str:
        """提取简短主题"""
        topic = user_msg[:10]
        if len(user_msg) > 10:
            topic += "..."
        return topic
    
    # ---- 上下文构建 ----
    
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
