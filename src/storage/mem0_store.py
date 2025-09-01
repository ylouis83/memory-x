"""Mem0-based implementation of MemoryStore.

This adapter wraps the `mem0` project (https://github.com/mem0ai/mem0)
so it can be used as a pluggable backend within Memory-X.  It requires
`mem0` to be installed; if the dependency is missing, importing this
module will raise an informative error.
"""

from __future__ import annotations

from typing import Dict, List, Optional

try:
    from mem0 import Memory  # type: ignore
    from mem0.configs.base import MemoryConfig  # type: ignore
except Exception as exc:  # pragma: no cover - handled in tests
    raise ImportError(
        "mem0 is required for Mem0MemoryStore. Install with"
        " `pip install git+https://github.com/mem0ai/mem0.git`"
    ) from exc

from .base import MemoryStore


class Mem0MemoryStore(MemoryStore):
    """Persist and search memories using the mem0 project."""

    def __init__(self, config: Optional[MemoryConfig] = None) -> None:
        self.memory = Memory(config or MemoryConfig())

    def add_conversation(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        entities: Optional[Dict] = None,
        intent: Optional[str] = None,
        importance: int = 1,
    ) -> None:
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response},
        ]
        # mem0 handles embedding and storage internally
        self.memory.add(messages, user_id=user_id)

    def get_stats(self, user_id: str) -> Dict:
        try:
            res = self.memory.search("", user_id=user_id, limit=1000)
            total = len(res.get("results", []))
        except Exception:
            total = 0
        return {"total_long_term": total}

    def search_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict]:
        res = self.memory.search(query, user_id=user_id, limit=top_k)
        results: List[Dict] = []
        for item in res.get("results", []):
            results.append({
                "content": item.get("memory", ""),
                "score": item.get("score", 0.0),
            })
        return results
