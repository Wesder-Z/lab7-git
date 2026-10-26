from __future__ import annotations

from lab7_db.query_cache import cached_book_rows
from lab7_db.sqlite_repository import SQLiteLibraryRepository


def test_cached_select_is_invalidated_after_insert_and_delete(tmp_path):
    repository = SQLiteLibraryRepository(tmp_path / "library.sqlite3")
    repository.initialize()
    author_id = repository.add_author("Михаил Булгаков")

    assert repository.list_books(use_cache=True) == []
    book_id = repository.add_book("Мастер и Маргарита", author_id)
    assert repository.list_books(use_cache=True)[0].title == "Мастер и Маргарита"
    assert cached_book_rows.cache_info().currsize == 1

    assert repository.delete_book(book_id) is True
    assert repository.list_books(use_cache=True) == []
