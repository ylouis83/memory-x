"""
Memory-X 核心包
智能记忆管理系统
"""

__version__ = "1.0.0"
__author__ = "Memory-X Team"
__email__ = "memory-x@example.com"

"""Expose primary classes while avoiding hard-coded sensitive defaults."""

from .core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI

# Backwards compatibility: some code may reference ``MemoryManager``.
# Alias it to ``SimpleMemoryManager`` so imports continue to work.
MemoryManager = SimpleMemoryManager

__all__ = [
    'MemoryManager',
    'SimpleMemoryManager',
    'SimpleMemoryIntegratedAI'
]
