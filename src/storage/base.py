"""Abstract interfaces for memory storage backends."""

from __future__ import annotations

from typing import Dict, List, Optional


class MemoryStore:
    """Interface for persistent memory storage backends.

    The interface models the capabilities of Vertex AI's Memory Bank and
    exposes a minimal set of operations used by the agent.  In addition to
    persisting conversations and returning statistics, stores may provide
    lightweight content search to retrieve relevant context for a query.
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

    def search_memories(
        self, user_id: str, query: str, limit: int = 5
    ) -> List[Dict]:
        """Return memories matching ``query`` for ``user_id``.

        Implementations can use simple keyword search or more advanced
        semantic retrieval.  Results are ordered by relevance or recency.
        """
        raise NotImplementedError
