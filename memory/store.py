import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class MemoryStore:
    """Markdown 文件存储（真实来源）"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(os.path.expanduser(data_dir))
        self.conversations_dir = self.data_dir / "conversations"
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_today_file(self) -> Path:
        """获取今日日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.conversations_dir / f"{today}.md"
    
    def _get_date_file(self, date_str: str) -> Path:
        """获取指定日期的日志文件"""
        return self.conversations_dir / f"{date_str}.md"
    
    def append_message(self, role: str, content: str, timestamp: datetime = None):
        """追加单条消息到今日日志"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%H:%M")
        role_label = "用户" if role == "user" else "助手"
        
        file_path = self._get_today_file()
        
        # 如果文件不存在，创建文件头
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {timestamp.strftime('%Y-%m-%d')} 对话记录\n\n")
        
        # 追加消息
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"## {time_str}\n")
            f.write(f"**{role_label}**: {content}\n\n")
    
    def append_conversation(self, user_msg: str, assistant_msg: str, 
                           timestamp: datetime = None):
        """追加一轮对话（用户+助手）"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%H:%M")
        topic = self._extract_topic(user_msg)
        
        file_path = self._get_today_file()
        
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {timestamp.strftime('%Y-%m-%d')} 对话记录\n\n")
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"## {time_str} — {topic}\n")
            f.write(f"**用户**: {user_msg}\n")
            f.write(f"**助手**: {assistant_msg}\n\n")
    
    def _extract_topic(self, user_msg: str) -> str:
        """从用户消息中提取简短主题"""
        # 简单实现：取前10个字符
        topic = user_msg[:10]
        if len(user_msg) > 10:
            topic += "..."
        return topic
    
    def read_day(self, date_str: str) -> str:
        """读取指定日期的完整日志"""
        file_path = self._get_date_file(date_str)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def list_days(self) -> List[str]:
        """列出所有有日志的日期"""
        days = []
        for file_path in self.conversations_dir.glob("*.md"):
            if file_path.stem != "MEMORY":
                days.append(file_path.stem)
        return sorted(days, reverse=True)
    
    def read_recent(self, n: int = 3) -> str:
        """读取最近 n 天的日志"""
        days = self.list_days()[:n]
        result = []
        for day in days:
            content = self.read_day(day)
            if content:
                result.append(content)
        return "\n---\n".join(result)
    
    def get_long_term_memory(self) -> str:
        """读取长期记忆"""
        file_path = self.data_dir / "MEMORY.md"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def append_long_term_memory(self, content: str):
        """追加内容到长期记忆"""
        file_path = self.data_dir / "MEMORY.md"
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# 长期记忆\n\n")
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"- {datetime.now().strftime('%Y-%m-%d')}: {content}\n")
