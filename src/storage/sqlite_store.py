"""SQLite implementation of :class:`MemoryStore`."""

from __future__ import annotations

import json
import math
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from .base import MemoryStore


class SQLiteMemoryStore(MemoryStore):
    """Persist memory using a local SQLite database."""

    def __init__(self, db_path: str = "data/simple_memory.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT NOT NULL,
                importance INTEGER NOT NULL,
                entities TEXT,
                intent TEXT,
                timestamp TEXT NOT NULL,
                embedding TEXT
            )
            """
        )
        cursor.execute("PRAGMA table_info(memories)")
        cols = [row[1] for row in cursor.fetchall()]
        if "embedding" not in cols:
            cursor.execute("ALTER TABLE memories ADD COLUMN embedding TEXT")
        conn.commit()
        conn.close()

    def add_conversation(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        entities: Optional[Dict] = None,
        intent: Optional[str] = None,
        importance: int = 1,
    ) -> None:
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []
        for content, mtype in ((user_message, "user"), (ai_response, "ai")):
            embedding = json.dumps(self._embed(content))
            records.append(
                (
                    user_id,
                    content,
                    mtype,
                    importance,
                    json.dumps(entities),
                    intent,
                    now,
                    embedding,
                )
            )
        cursor.executemany(
            """
            INSERT INTO memories
            (user_id, content, message_type, importance, entities, intent, timestamp, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()
        conn.close()

    def get_stats(self, user_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM memories WHERE user_id = ?",
            (user_id,),
        )
        total_long_term = cursor.fetchone()[0]
        conn.close()
        return {"total_long_term": total_long_term}

    # Retrieval -----------------------------------------------------------------
    @staticmethod
    def _embed(text: str) -> List[float]:
        """Simple character frequency embedding used for tests.

        The vector dimension is fixed at 26 (letters a-z)."""
        vec = [0.0] * 26
        for ch in text.lower():
            if "a" <= ch <= "z":
                vec[ord(ch) - 97] += 1.0
        return vec

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT content, embedding, message_type, importance, entities, intent, timestamp 
            FROM memories WHERE user_id = ?
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        query_vec = self._embed(query)
        results: List[Dict] = []
        
        # 按对话对组织记忆
        conversation_pairs = {}
        for content, emb_text, message_type, importance, entities_str, intent, timestamp in rows:
            try:
                emb = json.loads(emb_text) if emb_text else []
            except json.JSONDecodeError:
                emb = []
            score = self._cosine(query_vec, emb)
            
            # 按时间戳分组
            if timestamp not in conversation_pairs:
                conversation_pairs[timestamp] = {'user': None, 'ai': None, 'score': 0, 'importance': importance, 'entities': entities_str, 'intent': intent}
            
            if message_type == 'user':
                conversation_pairs[timestamp]['user'] = content
                conversation_pairs[timestamp]['score'] = max(conversation_pairs[timestamp]['score'], score)
            elif message_type == 'ai':
                conversation_pairs[timestamp]['ai'] = content
                conversation_pairs[timestamp]['score'] = max(conversation_pairs[timestamp]['score'], score)
        
        # 转换为前端期望的格式
        for timestamp, pair in conversation_pairs.items():
            if pair['user'] and pair['ai']:  # 只返回完整的对话
                try:
                    entities = json.loads(pair['entities']) if pair['entities'] else {}
                except json.JSONDecodeError:
                    entities = {}
                
                results.append({
                    "user_message": pair['user'],
                    "ai_response": pair['ai'],
                    "timestamp": timestamp,
                    "importance": pair['importance'],
                    "entities": entities,
                    "intent": pair['intent'],
                    "score": pair['score']
                })
        
        conn.close()
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    # Additional helpers --------------------------------------------------------
    def delete_by_pattern(self, user_id: str, pattern: str) -> int:
        """Delete memories whose content LIKE ``pattern`` for a given user.

        Returns the number of rows deleted.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM memories WHERE user_id = ? AND content LIKE ?",
            (user_id, pattern),
        )
        deleted = cursor.rowcount or 0
        conn.commit()
        conn.close()
        return deleted
