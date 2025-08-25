"""
Memory-X 核心包
智能记忆管理系统
"""

__version__ = "1.0.0"
__author__ = "Memory-X Team"
__email__ = "memory-x@example.com"

from .core.memory_manager import MemoryManager, SimpleMemoryIntegratedAI

__all__ = [
    'MemoryManager',
    'SimpleMemoryIntegratedAI'
]
