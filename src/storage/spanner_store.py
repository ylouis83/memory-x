"""Cloud Spanner implementation of :class:`MemoryStore`.

This backend is inspired by Google Vertex AI's memory design. It
shows how conversation turns could be persisted in a globally
distributed database. The actual connection details are left as
placeholders so tests can run without Cloud Spanner access.
"""

from __future__ import annotations

from typing import Dict, List, Optional

try:  # pragma: no cover - optional dependency
    from google.cloud import spanner  # type: ignore
except Exception:  # pragma: no cover - fallback when library not installed
    spanner = None

from .base import MemoryStore


class SpannerMemoryStore(MemoryStore):
    """Illustrative Cloud Spanner backend.

    Parameters are kept minimal; in real deployments you would
    configure credentials, instance/database IDs and use strong
    transactions for consistency.
    """

    def __init__(self, instance_id: str, database_id: str) -> None:
        self.instance_id = instance_id
        self.database_id = database_id
        self.client = None
        if spanner is not None:  # pragma: no cover - requires external service
            self.client = spanner.Client()
            self.instance = self.client.instance(instance_id)
            self.database = self.instance.database(database_id)

    def add_conversation(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        entities: Optional[Dict] = None,
        intent: Optional[str] = None,
        importance: int = 1,
    ) -> None:  # pragma: no cover - illustrative only
        if self.client is None:
            raise RuntimeError("google-cloud-spanner is not installed")
        # Placeholder mutation; in production you'd use parameterised SQL
        with self.database.batch() as batch:
            batch.insert(
                table="memories",
                columns=(
                    "user_id",
                    "content",
                    "message_type",
                    "importance",
                    "entities",
                    "intent",
                    "timestamp",
                ),
                values=[
                    (
                        user_id,
                        user_message,
                        "user",
                        importance,
                        str(entities),
                        intent,
                        "CURRENT_TIMESTAMP",
                    ),
                    (
                        user_id,
                        ai_response,
                        "ai",
                        importance,
                        str(entities),
                        intent,
                        "CURRENT_TIMESTAMP",
                    ),
                ],
            )

    def get_stats(self, user_id: str) -> Dict:  # pragma: no cover - illustrative
        if self.client is None:
            # Without the spanner library we can't query real data
            return {"total_long_term": 0}
        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                "SELECT COUNT(*) FROM memories WHERE user_id=@uid",
                params={"uid": user_id},
                param_types={"uid": spanner.param_types.STRING},
            )
            row = list(result)[0]
            return {"total_long_term": row[0]}

    def search_memories(
        self, user_id: str, query: str, limit: int = 5
    ) -> List[Dict]:  # pragma: no cover - illustrative
        if self.client is None:
            return []
        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                """
                SELECT content, message_type, importance, entities, intent, timestamp
                FROM memories
                WHERE user_id=@uid AND content LIKE @q
                ORDER BY timestamp DESC
                LIMIT @lim
                """,
                params={"uid": user_id, "q": f"%{query}%", "lim": limit},
                param_types={
                    "uid": spanner.param_types.STRING,
                    "q": spanner.param_types.STRING,
                    "lim": spanner.param_types.INT64,
                },
            )
            rows = list(result)
            return [
                {
                    "content": r[0],
                    "message_type": r[1],
                    "importance": r[2],
                    "entities": r[3],
                    "intent": r[4],
                    "timestamp": r[5],
                }
                for r in rows
            ]
