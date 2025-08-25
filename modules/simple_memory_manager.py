"""Compatibility layer for tests expecting modules.simple_memory_manager.

This module re-exports memory manager classes from src.core.memory_manager
so that existing import paths remain valid without exposing implementation
secrets or sensitive default credentials.
"""

from src.core.memory_manager import (
    SimpleMemoryIntegratedAI,
    SimpleMemoryManager,
)

__all__ = ["SimpleMemoryIntegratedAI", "SimpleMemoryManager"]
