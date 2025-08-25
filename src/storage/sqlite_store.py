"""SQLite implementation of :class:`MemoryStore`."""

from __future__ import annotations

import json
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
                timestamp TEXT NOT NULL
            )
            """
        )
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
        """Persist both sides of a conversation turn.

        Each message is stored as a separate row so that simple keyword
        search can retrieve past user or assistant messages similarly to
        Vertex AI's Memory Bank."""
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO memories
            (user_id, content, message_type, importance, entities, intent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    user_id,
                    user_message,
                    "user",
                    importance,
                    json.dumps(entities),
                    intent,
                    now,
                ),
                (
                    user_id,
                    ai_response,
                    "ai",
                    importance,
                    json.dumps(entities),
                    intent,
                    now,
                ),
            ],
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

    def search_memories(
        self, user_id: str, query: str, limit: int = 5
    ) -> List[Dict]:
        """Naively search for memories containing ``query``.

        Uses SQL ``LIKE`` which is sufficient for tests and demonstrates the
        retrieval API of Vertex AI's Memory Bank."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT content, message_type, importance, entities, intent, timestamp
            FROM memories
            WHERE user_id = ? AND content LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, f"%{query}%", limit),
        )
        rows = cursor.fetchall()
        conn.close()
        results: List[Dict] = []
        for row in rows:
            content, message_type, importance, entities, intent, ts = row
            results.append(
                {
                    "content": content,
                    "message_type": message_type,
                    "importance": importance,
                    "entities": json.loads(entities) if entities else {},
                    "intent": intent,
                    "timestamp": ts,
                }
            )
        return results
