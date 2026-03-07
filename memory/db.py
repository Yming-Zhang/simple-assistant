import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class MemoryDB:
    """SQLite 元数据存储（暂不做向量）"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    topic TEXT
                )
            ''')
            
            # 索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date_str)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            
            conn.commit()
    
    def insert_message(self, timestamp: datetime, role: str, content: str, 
                      topic: Optional[str] = None):
        """插入单条消息"""
        date_str = timestamp.strftime("%Y-%m-%d")
        timestamp_str = timestamp.isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (timestamp, date_str, role, content, topic)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp_str, date_str, role, content, topic))
            conn.commit()
            return cursor.lastrowid
    
    def insert_conversation(self, timestamp: datetime, user_msg: str, 
                           assistant_msg: str, topic: Optional[str] = None):
        """插入一轮对话"""
        self.insert_message(timestamp, "user", user_msg, topic)
        self.insert_message(timestamp, "assistant", assistant_msg, topic)
    
    def get_recent_messages(self, n: int = 20) -> List[Dict[str, Any]]:
        """获取最近 n 条消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (n,))
            rows = cursor.fetchall()
        
        # 反转顺序（旧到新）
        result = []
        for row in reversed(rows):
            result.append(dict(row))
        return result
    
    def get_messages_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """获取指定日期的所有消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE date_str = ?
                ORDER BY timestamp ASC
            ''', (date_str,))
            rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取日期范围内的消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE date_str BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_date, end_date))
            rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
