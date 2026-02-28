"""
Database Layer - MongoDB Operations
Provides data access layer with Repository Pattern
"""

from .connection import get_database, close_connection
from .repositories import (
    UserProfileRepository,
    UserSnapshotRepository,
    UserEmbeddingRepository,
    NoteEmbeddingRepository,
    CreatorNetworkRepository,
    StylePromptRepository,
    PlatformConfigRepository
)

__all__ = [
    'get_database',
    'close_connection',
    'UserProfileRepository',
    'UserSnapshotRepository',
    'UserEmbeddingRepository',
    'NoteEmbeddingRepository',
    'CreatorNetworkRepository',
    'StylePromptRepository',
    'PlatformConfigRepository'
]
