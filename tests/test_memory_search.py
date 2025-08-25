#!/usr/bin/env python3
"""Tests for vector-based memory retrieval."""

from modules.simple_memory_manager import SimpleMemoryManager


def test_memory_retrieval_similarity():
    mgr = SimpleMemoryManager("user_test")
    # ensure persistence by using high importance
    mgr.add_conversation("I love apples", "ok", importance=3)
    mgr.add_conversation("The cat sat on the mat", "ok", importance=3)
    results = mgr.retrieve_memories("apples")
    assert results
    assert results[0]["content"].startswith("I love apples")
