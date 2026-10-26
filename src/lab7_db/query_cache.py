"""Кэширование результатов запросов к SQLite."""

from __future__ import annotations

import sqlite3
from functools import lru_cache


@lru_cache(maxsize=128)
def cached_book_rows(database_path: str) -> tuple[tuple[int, str, str], ...]:
    """Вернуть строки книг из SQLite и сохранить результат в памяти."""
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT books.id, books.title, authors.name
            FROM books
            JOIN authors ON authors.id = books.author_id
            ORDER BY books.id
            """
        ).fetchall()

    return tuple(
        (int(book_id), str(title), str(author_name))
        for book_id, title, author_name in rows
    )


def clear_query_cache() -> None:
    """Очистить кэш после изменения данных в базе."""
    cached_book_rows.cache_clear()
