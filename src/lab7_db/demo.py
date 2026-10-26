"""Демонстрация операций SQLite без внешнего сервера."""

from __future__ import annotations

from tempfile import TemporaryDirectory

from .sqlite_repository import SQLiteLibraryRepository


def main() -> None:
    """Создать временную БД, показать вставку, кэш и удаление."""
    with TemporaryDirectory() as temporary_directory:
        database_path = f"{temporary_directory}/library.sqlite3"
        repository = SQLiteLibraryRepository(database_path)
        repository.initialize()

        author_id = repository.add_author("Александр Пушкин")
        book_id = repository.add_book("Капитанская дочка", author_id)

        print("Книги после вставки:", repository.list_books())
        print("Повторная выборка из кэша:", repository.list_books(use_cache=True))
        print("Удаление выполнено:", repository.delete_book(book_id))
        print("Книги после удаления:", repository.list_books(use_cache=True))


if __name__ == "__main__":
    main()
