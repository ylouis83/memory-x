"""SQLite implementation of :class:`MemoryStore`."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Optional

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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO memories
            (user_id, content, message_type, importance, entities, intent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user_message,
                "user",
                importance,
                json.dumps(entities),
                intent,
                datetime.now().isoformat(),
            ),
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
