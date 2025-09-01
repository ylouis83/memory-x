import importlib
import pytest

try:
    import mem0  # noqa: F401
    MEM0_AVAILABLE = True
except Exception:  # pragma: no cover - handled in skip
    MEM0_AVAILABLE = False


@pytest.mark.skipif(not MEM0_AVAILABLE, reason="mem0 not installed")
def test_mem0_store_roundtrip():
    from src.storage.mem0_store import Mem0MemoryStore

    store = Mem0MemoryStore()
    store.add_conversation("u1", "hello there", "hi")
    stats = store.get_stats("u1")
    assert stats["total_long_term"] >= 2
    results = store.search_memories("u1", "hello")
    assert any("hello" in r["content"] for r in results)
