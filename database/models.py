"""
Модуль описания таблиц базы данных и вспомогательные функции.

Таблицы:
- statistics — информация о загрузках
- managers — список менеджеров
- processing_history — история обработок файлов
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def _db_cursor(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn, conn.cursor()
        conn.commit()
    finally:
        conn.close()


def init_database(db_path: str) -> None:
    """
    Инициализирует базу данных, создаёт таблицы если не существуют.

    Args:
        db_path: Путь к файлу базы данных
    """
    with _db_cursor(db_path) as (_, cursor):
        # Таблица statistics
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            load_date TEXT NOT NULL,
            leads_count INTEGER DEFAULT 0,
            unique_phones INTEGER DEFAULT 0,
            segment TEXT,
            region TEXT
        )
    """)

        # Таблица managers
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

        # Таблица processing_history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            process_date TEXT NOT NULL,
            rows_processed INTEGER DEFAULT 0,
            duplicates_removed INTEGER DEFAULT 0,
            processing_time_ms INTEGER DEFAULT 0
        )
    """)

        # Создаём индексы для ускорения запросов
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_statistics_filename ON statistics(filename)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_statistics_load_date ON statistics(load_date)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_managers_name ON managers(name)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_managers_active ON managers(is_active)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_processing_history_date ON processing_history(process_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_processing_history_filename ON processing_history(filename)"
        )


def save_statistics(
    db_path: str,
    filename: str,
    leads_count: int,
    unique_phones: int,
    segment: str | None = None,
    region: str | None = None,
) -> None:
    """
    Сохраняет статистику по загрузке файла.

    Args:
        db_path: Путь к базе данных
        filename: Имя файла
        leads_count: Количество лидов
        unique_phones: Количество уникальных телефонов
        segment: Сегмент (опционально)
        region: Регион (опционально)
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute(
            """
            INSERT INTO statistics (filename, load_date, leads_count, unique_phones, segment, region)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                filename,
                datetime.now().isoformat(),
                leads_count,
                unique_phones,
                segment,
                region,
            ),
        )


def save_manager(db_path: str, name: str, is_active: bool = True) -> None:
    """
    Сохраняет или обновляет менеджера в базе.

    Args:
        db_path: Путь к базе данных
        name: Имя менеджера
        is_active: Активен ли менеджер
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute(
            """
            INSERT OR REPLACE INTO managers (name, is_active, created_at)
            VALUES (?, ?, ?)
        """,
            (name, 1 if is_active else 0, datetime.now().isoformat()),
        )


def clear_managers(db_path: str) -> None:
    """
    Очищает таблицу менеджеров.

    Args:
        db_path: Путь к базе данных
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute("DELETE FROM managers")


def get_managers(db_path: str) -> list[str]:
    """
    Получает список активных менеджеров.

    Args:
        db_path: Путь к базе данных

    Returns:
        Список имён менеджеров
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute("SELECT name FROM managers WHERE is_active = 1")
        managers = [row[0] for row in cursor.fetchall()]

    return managers


def save_processing_history(
    db_path: str,
    filename: str,
    rows_processed: int,
    duplicates_removed: int,
    processing_time_ms: int,
) -> None:
    """
    Сохраняет историю обработки файла.

    Args:
        db_path: Путь к базе данных
        filename: Имя файла
        rows_processed: Количество обработанных строк
        duplicates_removed: Количество удалённых дубликатов
        processing_time_ms: Время обработки в миллисекундах
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute(
            """
            INSERT INTO processing_history (filename, process_date, rows_processed, duplicates_removed, processing_time_ms)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                filename,
                datetime.now().isoformat(),
                rows_processed,
                duplicates_removed,
                processing_time_ms,
            ),
        )


def get_processing_history(db_path: str, limit: int = 100) -> list[dict]:
    """
    Получает историю обработок.

    Args:
        db_path: Путь к базе данных
        limit: Максимальное количество записей

    Returns:
        Список словарей с историей обработок
    """
    with _db_cursor(db_path) as (_, cursor):
        cursor.execute(
            """
            SELECT filename, process_date, rows_processed, duplicates_removed, processing_time_ms
            FROM processing_history
            ORDER BY process_date DESC
            LIMIT ?
        """,
            (limit,),
        )

        history = [
            {
                "filename": row[0],
                "process_date": row[1],
                "rows_processed": row[2],
                "duplicates_removed": row[3],
                "processing_time_ms": row[4],
            }
            for row in cursor.fetchall()
        ]

    return history
