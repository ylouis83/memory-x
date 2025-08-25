"""Abstract interfaces for memory storage backends."""

from __future__ import annotations

from typing import Dict, List, Optional


class MemoryStore:
    """Interface for persistent memory storage backends.

    The interface models the capabilities of Vertex AI's Memory Bank and
    supports both persistence and lightweight content search. Concrete
    backends should implement the following operations:

    * ``add_conversation`` – persist a single conversation turn
    * ``get_stats`` – return aggregated statistics for a user
    * ``search_memories`` – retrieve relevant memories for a query
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

    # Retrieval -----------------------------------------------------------------
    def search_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """Return up to ``top_k`` memories matching ``query``.

        Implementations may use simple keyword search or embedding similarity
        depending on their capabilities.
        """
        raise NotImplementedError
