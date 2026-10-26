from __future__ import annotations

import sqlite3

import pytest

from lab7_db.sqlite_repository import SQLiteLibraryRepository


def test_initialize_creates_two_related_tables_and_supports_operations(tmp_path):
    repository = SQLiteLibraryRepository(tmp_path / "library.sqlite3")
    repository.initialize()

    author_id = repository.add_author("  Антон Чехов ")
    book_id = repository.add_book("Вишнёвый сад", author_id)
    books = repository.list_books()

    assert len(books) == 1
    assert books[0].id == book_id
    assert books[0].title == "Вишнёвый сад"
    assert books[0].author_name == "Антон Чехов"
    assert repository.delete_book(book_id) is True
    assert repository.list_books() == []


def test_database_has_authors_and_books_tables_with_foreign_key(tmp_path):
    database_path = tmp_path / "library.sqlite3"
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()

    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        foreign_keys = connection.execute("PRAGMA foreign_key_list(books)").fetchall()

    assert {"authors", "books"} <= table_names
    assert foreign_keys


def test_delete_missing_book_returns_false(tmp_path):
    repository = SQLiteLibraryRepository(tmp_path / "library.sqlite3")
    repository.initialize()

    assert repository.delete_book(404) is False


def test_validation_rejects_empty_values_and_unknown_author(tmp_path):
    repository = SQLiteLibraryRepository(tmp_path / "library.sqlite3")
    repository.initialize()

    with pytest.raises(ValueError):
        repository.add_author("   ")
    with pytest.raises(ValueError):
        repository.add_book("Книга", 999)
