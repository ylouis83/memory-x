"""Abstract interfaces for memory storage backends."""

from __future__ import annotations

from typing import Dict, Optional


class MemoryStore:
    """Interface for persistent memory storage backends.

    A store only needs to implement two operations for the current
    simplified agent memory:

    * ``add_conversation`` – persist a single conversation turn
    * ``get_stats`` – return aggregated statistics for a user
    """

    def add_conversation(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        entities: Optional[Dict] = None,
        intent: Optional[str] = None,
        importance: int = 1,
    ) -> None:
        raise NotImplementedError

    def get_stats(self, user_id: str) -> Dict:
        raise NotImplementedError
