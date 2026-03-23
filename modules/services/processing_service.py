"""
Сервисный слой для обработки лидов.

Этот модуль предоставляет абстракции между GUI и бизнес-логикой,
обеспечивая Dependency Injection и упрощая тестирование.
"""

import time
from pathlib import Path
from typing import Protocol, runtime_checkable
import pandas as pd
import logging

from modules.data_processor import merge_files, remove_duplicates, assign_managers
from modules.bitrix_mapper import map_to_bitrix, export_to_bitrix_csv
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


@runtime_checkable
class IDatabaseManager(Protocol):
    """Протокол для менеджера базы данных."""
    
    def add_processing_record(
        self,
        filename: str,
        rows_processed: int,
        duplicates_removed: int,
        processing_time_ms: int,
    ) -> None: ...


class ProcessingService:
    """
    Сервис для обработки лидов.
    
    Example:
        >>> db_manager = DatabaseManager("data/database.db")
        >>> service = ProcessingService(db_manager, config)
        >>> df, stats = service.process_files(["file1.json"], ["Manager 1"])
    """
    
    def __init__(
        self,
        db_manager: IDatabaseManager,
        config: dict,
    ):
        """
        Инициализирует сервис.
        
        Args:
            db_manager: Менеджер базы данных (или mock для тестов)
            config: Конфигурация приложения
        """
        self._db = db_manager
        self._config = config
    
    def process_files(
        self,
        file_paths: list[str],
        managers: list[str],
    ) -> tuple[pd.DataFrame, dict]:
        """
        Обрабатывает файлы и возвращает результат для Битрикс24.
        
        Args:
            file_paths: Список путей к файлам
            managers: Список имён менеджеров
            
        Returns:
            Кортеж (DataFrame для Битрикс, статистика)
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если данные невалидны
        """
        # Валидация входных данных
        self._validate_files(file_paths)
        
        if not managers:
            raise ValueError("Список менеджеров не может быть пустым")
        
        # Замер времени
        start_time = time.time()
        
        # Обработка файлов
        processing_settings = self._config.get("processing", {})
        df, stats = merge_files(file_paths, managers, processing_settings)
        
        if df.empty:
            raise ValueError("Обработанные данные пусты")
        
        # Маппинг для Битрикс
        bitrix_settings = self._config.get("bitrix", {})
        df_bitrix = map_to_bitrix(df, **bitrix_settings)
        
        # Замер времени окончания
        processing_time_ms = int((time.time() - start_time) * 1000)
        stats["processing_time_ms"] = processing_time_ms
        
        # Сохранение в БД
        self._save_to_database(file_paths, stats)
        
        return df_bitrix, stats
    
    def export_to_csv(
        self,
        df: pd.DataFrame,
        filepath: str,
    ) -> str:
        """
        Экспортирует DataFrame в CSV файл.
        
        Args:
            df: DataFrame с данными
            filepath: Путь для сохранения файла
            
        Returns:
            Путь к сохранённому файлу
            
        Raises:
            IOError: Если не удалось сохранить файл
        """
        if not export_to_bitrix_csv(df, filepath):
            raise IOError(f"Не удалось экспортировать файл: {filepath}")
        
        return filepath
    
    def _validate_files(self, file_paths: list[str]) -> None:
        """Проверяет существование файлов."""
        for path in file_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"Файл не найден: {path}")
    
    def _save_to_database(self, file_paths: list[str], stats: dict) -> None:
        """Сохраняет статистику обработки в БД."""
        try:
            filename = ", ".join(Path(f).name for f in file_paths)
            self._db.add_processing_record(
                filename=filename,
                rows_processed=stats.get("total_rows", 0),
                duplicates_removed=stats.get("duplicates_removed", 0),
                processing_time_ms=stats.get("processing_time_ms", 0),
            )
        except Exception as e:
            # Логгируем ошибку, но не прерываем обработку
            logger.error(f"Ошибка сохранения в БД: {e}")
