"""
Memory-X 核心模块
包含记忆管理的核心功能
"""

from .memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI

# Alias for backward compatibility
MemoryManager = SimpleMemoryManager

__all__ = [
    'MemoryManager',
    'SimpleMemoryManager',
    'SimpleMemoryIntegratedAI'
]
