"""Учебный пакет для работы с SQLite и PostgreSQL."""

from .sqlite_repository import BookRecord, SQLiteLibraryRepository

__all__ = ["BookRecord", "SQLiteLibraryRepository"]
