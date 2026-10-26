"""Репозиторий SQLite для библиотеки с двумя связанными таблицами."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .query_cache import cached_book_rows, clear_query_cache


@dataclass(frozen=True, slots=True)
class BookRecord:
    """Неизменяемое представление книги из результата запроса."""

    id: int
    title: str
    author_name: str


class SQLiteLibraryRepository:
    """Выполнять основные операции с таблицами authors и books."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(Path(database_path))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Создать базу и связанные таблицы, если их ещё нет."""
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
                );

                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                    author_id INTEGER NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES authors (id)
                        ON DELETE CASCADE
                );
                """
            )

    def add_author(self, name: str) -> int:
        """Добавить автора или вернуть id уже существующего автора."""
        cleaned_name = self._require_text(name, "Имя автора")

        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO authors (name) VALUES (?)",
                (cleaned_name,),
            )
            row = connection.execute(
                "SELECT id FROM authors WHERE name = ?",
                (cleaned_name,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Не удалось получить id автора")
        return int(row["id"])

    def add_book(self, title: str, author_id: int) -> int:
        """Добавить книгу с параметризованным запросом и вернуть её id."""
        cleaned_title = self._require_text(title, "Название книги")
        if isinstance(author_id, bool) or not isinstance(author_id, int):
            raise TypeError("id автора должен быть целым числом")
        if author_id <= 0:
            raise ValueError("id автора должен быть положительным")

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    "INSERT INTO books (title, author_id) VALUES (?, ?)",
                    (cleaned_title, author_id),
                )
                book_id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError("Указанный автор не существует") from error

        clear_query_cache()
        if book_id is None:
            raise RuntimeError("SQLite не вернула id книги")
        return int(book_id)

    def list_books(self, use_cache: bool = False) -> list[BookRecord]:
        """Вернуть книги с именами авторов в порядке id."""
        if use_cache:
            rows = cached_book_rows(self.database_path)
            return [BookRecord(*row) for row in rows]

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT books.id, books.title, authors.name AS author_name
                FROM books
                JOIN authors ON authors.id = books.author_id
                ORDER BY books.id
                """
            ).fetchall()

        return [
            BookRecord(
                id=int(row["id"]),
                title=str(row["title"]),
                author_name=str(row["author_name"]),
            )
            for row in rows
        ]

    def delete_book(self, book_id: int) -> bool:
        """Удалить книгу по id и вернуть признак успешного удаления."""
        if isinstance(book_id, bool) or not isinstance(book_id, int):
            raise TypeError("id книги должен быть целым числом")

        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
            deleted = cursor.rowcount > 0

        if deleted:
            clear_query_cache()
        return deleted

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} должно быть строкой")
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} не может быть пустым")
        return cleaned_value
