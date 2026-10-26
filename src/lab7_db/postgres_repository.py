"""Репозиторий PostgreSQL через драйвер psycopg2."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import psycopg2


ConnectionFactory = Callable[[str], Any]


class PostgresLibraryRepository:
    """Выполнять операции с PostgreSQL по строке подключения DSN."""

    def __init__(
        self,
        dsn: str | None = None,
        connection_factory: ConnectionFactory | None = None,
    ) -> None:
        self.dsn = dsn or os.getenv("POSTGRES_DSN")
        if not self.dsn:
            raise ValueError(
                "Передайте dsn или задайте переменную окружения POSTGRES_DSN"
            )
        self._connection_factory = connection_factory or psycopg2.connect

    def _connect(self) -> Any:
        return self._connection_factory(self.dsn)

    def initialize(self) -> None:
        """Создать таблицы PostgreSQL с внешним ключом."""
        connection = self._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS authors (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(200) NOT NULL UNIQUE
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS books (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(300) NOT NULL,
                            author_id INTEGER NOT NULL REFERENCES authors(id)
                                ON DELETE CASCADE
                        )
                        """
                    )
        finally:
            connection.close()

    def add_author(self, name: str) -> int:
        """Добавить автора и вернуть его идентификатор."""
        cleaned_name = self._require_text(name, "Имя автора")
        connection = self._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO authors (name) VALUES (%s)
                        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                        """,
                        (cleaned_name,),
                    )
                    row = cursor.fetchone()
        finally:
            connection.close()

        if row is None:
            raise RuntimeError("PostgreSQL не вернула id автора")
        return int(row[0])

    def list_books(self) -> list[tuple[int, str, str]]:
        """Получить книги и имена авторов одним JOIN-запросом."""
        connection = self._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT books.id, books.title, authors.name
                        FROM books
                        JOIN authors ON authors.id = books.author_id
                        ORDER BY books.id
                        """
                    )
                    rows = cursor.fetchall()
        finally:
            connection.close()

        return [(int(row[0]), str(row[1]), str(row[2])) for row in rows]

    def delete_book(self, book_id: int) -> bool:
        """Удалить книгу параметризованным запросом."""
        connection = self._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                    deleted = cursor.rowcount > 0
        finally:
            connection.close()
        return deleted

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} должно быть строкой")
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} не может быть пустым")
        return cleaned_value
