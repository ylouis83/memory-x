"""Abstract interfaces for memory storage backends."""

from __future__ import annotations

from typing import Dict, List, Optional


class MemoryStore:
    """Interface for persistent memory storage backends.

    The interface now mirrors the design of Vertex AI's Memory Bank by
    supporting both persistence and vector based retrieval of memories.
    Concrete backends should implement the following operations:

    * ``add_conversation`` – persist a single conversation turn
    * ``get_stats`` – return aggregated statistics for a user
    * ``search_memories`` – retrieve relevant memories using simple
      embedding similarity
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
        """Return the ``top_k`` memories most similar to ``query``.

        Backends are free to choose the embedding and similarity strategy. The
        default SQLite implementation uses a trivial character frequency
        embedding so tests can run without external dependencies.
        """
        raise NotImplementedError
