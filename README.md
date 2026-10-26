# Лабораторная работа №7

**Борисов Анатолий Олегович, группа 221141, вариант 5, лабораторная №7**

Дисциплина: «Методы и технологии программирования».

## Выполненные задания

| Сложность | № | Реализация |
|---|---:|---|
| Средняя | 5 | удаление записи из таблицы `books` через `delete_book()` |
| Средняя | 7 | связанные таблицы `authors` и `books` в SQLite и PostgreSQL |
| Средняя | 1 | создание SQLite-БД и таблиц через `initialize()` |
| Повышенная | 6 | репозиторий PostgreSQL на `psycopg2` с параметризованными запросами |
| Повышенная | 8 | кэширование SELECT-запроса через `functools.lru_cache` |

## Структура

```text
lab7-git/
├── src/lab7_db/
│   ├── postgres_repository.py
│   ├── query_cache.py
│   ├── sqlite_repository.py
│   └── demo.py
├── tests/
├── tools/verify.py
├── main.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

`SQLiteLibraryRepository` работает с двумя таблицами. Между `books.author_id` и
`authors.id` задан внешний ключ с каскадным удалением. Значения пользователей
передаются в SQL отдельными параметрами, а не объединяются со строкой запроса.

`PostgresLibraryRepository` использует `psycopg2` и получает строку подключения
из аргумента конструктора или из переменной окружения `POSTGRES_DSN`.

Результат чтения книг кэшируется в `query_cache.py`. После вставки или удаления
книги кэш очищается, поэтому следующая выборка видит актуальное состояние БД.

## Установка и запуск

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python main.py
```

Демонстрация использует временную SQLite-БД и не требует запущенного PostgreSQL.
Для подключения к PostgreSQL задайте DSN перед запуском собственного сценария:

```powershell
$env:POSTGRES_DSN = "postgresql://user:password@localhost:5432/library"
```

## Проверка

```powershell
python tools/verify.py
```

Скрипт выполняет компиляцию Python-файлов, проверку `flake8` и тесты `pytest`.
Тест PostgreSQL использует подменённое соединение, поэтому для автоматической
проверки не нужен отдельный сервер.
