from __future__ import annotations

from lab7_db.postgres_repository import PostgresLibraryRepository


class FakeCursor:
    def __init__(self) -> None:
        self.commands: list[tuple[str, object]] = []
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, parameters=None) -> None:
        self.commands.append((query, parameters))

    def fetchone(self):
        return (7,)

    def fetchall(self):
        return [(7, "Книга", "Автор")]


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return self.cursor_instance

    def close(self) -> None:
        self.closed = True


def test_postgres_repository_uses_dsn_and_parameterized_queries():
    connection = FakeConnection()
    repository = PostgresLibraryRepository(
        "postgresql://user:password@localhost/library",
        connection_factory=lambda dsn: connection,
    )

    repository.initialize()
    repository.add_author("Автор")
    repository.list_books()
    repository.delete_book(7)

    commands = connection.cursor_instance.commands
    assert any("%s" in query for query, _ in commands)
    assert any(parameters == ("Автор",) for _, parameters in commands)
    assert connection.closed is True
