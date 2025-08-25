"""Storage backends for Memory-X.

Provides a pluggable interface so different databases can be
used for long‑term memory storage. The default backend uses
SQLite for local testing, while a Cloud Spanner backend can be
used for horizontally scalable deployments inspired by Google
Vertex AI's design.
"""

from .base import MemoryStore
from .sqlite_store import SQLiteMemoryStore
from .spanner_store import SpannerMemoryStore

__all__ = [
    "MemoryStore",
    "SQLiteMemoryStore",
    "SpannerMemoryStore",
]
