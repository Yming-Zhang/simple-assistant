import sqlite3
import json
import uuid
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
        """初始化数据库表（含迁移）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '新对话',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_deleted INTEGER NOT NULL DEFAULT 0
                )
            ''')
            
            # 消息表（增加 conversation_id 外键）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    timestamp TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    topic TEXT,
                    images TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            ''')
            
            # 设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 迁移：为已有 messages 表添加新列（如果不存在）
            try:
                cursor.execute('SELECT conversation_id FROM messages LIMIT 1')
            except sqlite3.OperationalError:
                cursor.execute('ALTER TABLE messages ADD COLUMN conversation_id TEXT')
            try:
                cursor.execute('SELECT images FROM messages LIMIT 1')
            except sqlite3.OperationalError:
                cursor.execute('ALTER TABLE messages ADD COLUMN images TEXT')
            
            # 索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date_str)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at)')
            
            conn.commit()
    
    # ---- 会话 CRUD ----
    
    def create_conversation(self, title: str = "新对话") -> str:
        """创建新会话，返回 conversation_id"""
        conv_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (conv_id, title, now, now))
            conn.commit()
        return conv_id
    
    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """列出所有未删除的会话，按更新时间倒序"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count,
                       (SELECT m.content FROM messages m WHERE m.conversation_id = c.id 
                        AND m.role = 'user' ORDER BY m.timestamp DESC LIMIT 1) as preview
                FROM conversations c
                WHERE c.is_deleted = 0
                ORDER BY c.updated_at DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """获取会话基本信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversations WHERE id = ? AND is_deleted = 0
            ''', (conv_id,))
            row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_conversation_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (conv_id,))
            rows = cursor.fetchall()
        
        result = []
        for row in rows:
            msg = dict(row)
            # 反序列化 images
            if msg.get('images'):
                try:
                    msg['images'] = json.loads(msg['images'])
                except:
                    msg['images'] = []
            else:
                msg['images'] = []
            result.append(msg)
        return result
    
    def rename_conversation(self, conv_id: str, title: str) -> bool:
        """重命名会话"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations SET title = ?, updated_at = ?
                WHERE id = ? AND is_deleted = 0
            ''', (title, now, conv_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_conversation(self, conv_id: str) -> bool:
        """软删除会话"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            ''', (now, conv_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def touch_conversation(self, conv_id: str):
        """更新会话的 updated_at"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations SET updated_at = ? WHERE id = ?
            ''', (now, conv_id))
            conn.commit()

    # ---- 消息操作 ----
    
    def insert_message(self, timestamp: datetime, role: str, content: str, 
                      topic: Optional[str] = None, conversation_id: Optional[str] = None,
                      images: Optional[List[str]] = None):
        """插入单条消息"""
        date_str = timestamp.strftime("%Y-%m-%d")
        timestamp_str = timestamp.isoformat()
        images_json = json.dumps(images) if images else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (conversation_id, timestamp, date_str, role, content, topic, images)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (conversation_id, timestamp_str, date_str, role, content, topic, images_json))
            conn.commit()
            msg_id = cursor.lastrowid
        
        # 更新会话时间
        if conversation_id:
            self.touch_conversation(conversation_id)
        
        return msg_id
    
    def insert_conversation(self, timestamp: datetime, user_msg: str, 
                           assistant_msg: str, topic: Optional[str] = None,
                           conversation_id: Optional[str] = None):
        """插入一轮对话"""
        self.insert_message(timestamp, "user", user_msg, topic, conversation_id)
        self.insert_message(timestamp, "assistant", assistant_msg, topic, conversation_id)
    
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
    
    # ---- 设置持久化 ----
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取单个设置项"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']
        return default
    
    def set_setting(self, key: str, value: Any):
        """设置单个设置项"""
        now = datetime.now().isoformat()
        value_json = json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?
            ''', (key, value_json, now, value_json, now))
            conn.commit()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            rows = cursor.fetchall()
        result = {}
        for row in rows:
            try:
                result[row['key']] = json.loads(row['value'])
            except:
                result[row['key']] = row['value']
        return result
    
    def update_all_settings(self, settings: Dict[str, Any]):
        """批量更新设置"""
        for key, value in settings.items():
            self.set_setting(key, value)
