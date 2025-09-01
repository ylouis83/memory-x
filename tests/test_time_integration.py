import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.memory_manager import SimpleMemoryManager
from src.storage.base import MemoryStore


class DummyStore(MemoryStore):
    def __init__(self):
        self.records = []

    def add_conversation(self, user_id, user_message, ai_response, entities=None, intent=None, importance=1):
        self.records.append({
            'user_id': user_id,
            'user_message': user_message,
            'ai_response': ai_response,
            'entities': entities or {},
            'intent': intent,
            'importance': importance,
        })

    def get_stats(self, user_id: str):
        return {'total_long_term': len(self.records)}

    def search_memories(self, user_id: str, query: str, top_k: int = 5):
        return []


def test_reject_fabricated_statement_from_persist():
    store = DummyStore()
    mgr = SimpleMemoryManager(user_id="u1", store=store)
    # Explicitly set importance high enough to trigger persist if valid
    text = "我刚才乱说病情，都是编的。"
    ok = mgr.add_conversation(text, ai_response="ok", entities={'SYMPTOM': [('头痛', 0, 2)]}, intent='NORMAL_CONSULTATION', importance=3)
    assert ok is True
    # Should not persist due to validator rejection
    assert len(store.records) == 0


def test_time_update_precision_and_keep_on_vague_followup():
    store = DummyStore()
    mgr = SimpleMemoryManager(user_id="u2", store=store)
    # First: 最近1周头痛 → should attach TIME with week_range
    ok1 = mgr.add_conversation("最近1周头痛", ai_response="ok", entities={'SYMPTOM': [('头痛', 0, 2)]}, importance=3)
    assert ok1 is True
    assert len(store.records) == 1
    first = store.records[-1]
    assert 'TIME' in first['entities']
    t1 = first['entities']['TIME'][0]
    assert t1['precision'] == 'week_range'

    # Second: 近期头痛 → should not downgrade precision
    ok2 = mgr.add_conversation("近期头痛", ai_response="ok", entities={'SYMPTOM': [('头痛', 0, 2)]}, importance=3)
    assert ok2 is True
    assert len(store.records) == 2
    second = store.records[-1]
    assert 'TIME' in second['entities']
    t2 = second['entities']['TIME'][0]
    # precision should remain at least week_range (no downgrade)
    assert t2['precision'] in ('week_range', 'day_range', 'exact_date')
    # Start should not be later than first start (keep or widen)
    assert t2['start'] <= t1['start']

