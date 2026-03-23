"""
Менеджер базы данных SQLite.

Обёртка над моделями для удобного управления подключением и операциями.
"""

from pathlib import Path
from collections.abc import Iterable

from .models import (
    init_database,
    save_statistics,
    save_manager,
    clear_managers,
    get_managers,
    save_processing_history,
    get_processing_history,
)


class DatabaseManager:
    """
    Менеджер для работы с базой данных SQLite.
    """

    def __init__(self, db_path: str):
        """
        Инициализирует менеджер базы данных.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path

        # Создаём директорию если не существует
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Инициализируем базу данных
        init_database(db_path)

    def add_statistics(
        self,
        filename: str,
        leads_count: int,
        unique_phones: int,
        segment: str | None = None,
        region: str | None = None,
    ) -> None:
        """
        Сохраняет статистику по загрузке файла.

        Args:
            filename: Имя файла
            leads_count: Количество лидов
            unique_phones: Количество уникальных телефонов
            segment: Сегмент (опционально)
            region: Регион (опционально)
        """
        save_statistics(self.db_path, filename, leads_count, unique_phones, segment, region)

    def add_manager(self, name: str, is_active: bool = True) -> None:
        """
        Добавляет менеджера в базу.

        Args:
            name: Имя менеджера
            is_active: Активен ли менеджер
        """
        normalized = self._normalize_manager_name(name)
        if not normalized:
            return
        save_manager(self.db_path, normalized, is_active)

    def clear_managers_list(self) -> None:
        """
        Очищает список менеджеров.
        """
        clear_managers(self.db_path)

    def get_active_managers(self) -> list[str]:
        """
        Получает список активных менеджеров.

        Returns:
            Список имён менеджеров
        """
        return get_managers(self.db_path)

    def save_managers(self, managers: Iterable[str]) -> None:
        """
        Сохраняет список менеджеров (очищает и добавляет заново).

        Args:
            managers: Список имён менеджеров
        """
        self.clear_managers_list()
        for manager in managers:
            self.add_manager(manager)

    @staticmethod
    def _normalize_manager_name(name: str) -> str:
        return name.strip() if name else ""

    def add_processing_record(
        self,
        filename: str,
        rows_processed: int,
        duplicates_removed: int,
        processing_time_ms: int,
    ) -> None:
        """
        Сохраняет запись в историю обработок.

        Args:
            filename: Имя файла
            rows_processed: Количество обработанных строк
            duplicates_removed: Количество удалённых дубликатов
            processing_time_ms: Время обработки в миллисекундах
        """
        save_processing_history(
            self.db_path,
            filename,
            rows_processed,
            duplicates_removed,
            processing_time_ms,
        )

    def get_history(self, limit: int = 100) -> list[dict]:
        """
        Получает историю обработок.

        Args:
            limit: Максимальное количество записей

        Returns:
            Список словарей с историей обработок
        """
        return get_processing_history(self.db_path, limit)
