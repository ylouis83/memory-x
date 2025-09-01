"""
Memory-X 核心模块
包含记忆管理的核心功能
"""

from .memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI
from .medical_memory import (
    MedicationEntry,
    upsert_medication_entry,
)

# Alias for backward compatibility
MemoryManager = SimpleMemoryManager

__all__ = [
    'MemoryManager',
    'SimpleMemoryManager',
    'SimpleMemoryIntegratedAI',
    'MedicationEntry',
    'upsert_medication_entry',
]
