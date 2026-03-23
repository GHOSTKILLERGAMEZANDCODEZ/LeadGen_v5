"""
Поток обработки файлов для GUI приложения.

Модуль предоставляет QThread для запуска обработки лидов
в фоновом режиме без блокировки интерфейса.

Classes:
    ProcessingThread: QThread для обработки файлов и распределения по менеджерам.

Example:
    >>> thread = ProcessingThread(service, file_paths, managers)
    >>> thread.finished.connect(self.on_processing_finished)
    >>> thread.start()
"""

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from modules.bitrix_mapper import export_to_bitrix_csv

if TYPE_CHECKING:
    from modules.services.processing_service import ProcessingService


class ProcessingThread(QThread):
    """
    Поток для обработки файлов в фоновом режиме.

    Запускает обработку лидов (очистка, нормализация, распределение)
    в отдельном потоке чтобы не блокировать GUI.

    Signals:
        finished: Обработка завершена (DataFrame, stats)
        error: Произошла ошибка (str)
        progress: Прогресс обработки (int, str)

    Example:
        >>> thread = ProcessingThread(service, ["file1.json"], ["Manager 1"])
        >>> thread.finished.connect(lambda df, stats: print(f"Processed {len(df)} leads"))
        >>> thread.start()
    """

    # Сигналы
    finished = Signal(object, dict)  # DataFrame, stats
    error = Signal(str)  # Сообщение об ошибке
    progress = Signal(int, str)  # Прогресс (0-100), текст статуса

    def __init__(
        self,
        service: "ProcessingService",
        file_paths: list[str],
        managers: list[str],
        processing_settings: dict | None = None,
        parent: QThread | None = None,
    ) -> None:
        """
        Инициализация потока обработки.

        Args:
            service: Сервис обработки (Dependency Injection)
            file_paths: Список путей к файлам для обработки
            managers: Список имён менеджеров для распределения
            processing_settings: Настройки обработки (phone_format, remove_duplicates, etc.)
            parent: Родительский объект
        """
        super().__init__(parent)
        self._service = service
        self._file_paths = file_paths
        self._managers = managers
        self._processing_settings = processing_settings or {}

    def run(self) -> None:
        """
        Запуск обработки файлов.

        Выполняет:
        1. Загрузку и очистку файлов
        2. Нормализацию телефонов
        3. Удаление дубликатов
        4. Распределение по менеджерам
        5. Маппинг для Битрикс
        6. Сохранение статистики в БД
        """
        try:
            total_files = len(self._file_paths)
            self.progress.emit(0, f"Начало обработки {total_files} файлов...")

            # Замер времени начала
            start_time = time.time()

            # ✅ Обработка через сервис
            self.progress.emit(20, "Загрузка и очистка данных...")
            df, stats = self._service.process_files(
                self._file_paths,
                self._managers,
            )

            # Проверка результата
            if df is None or len(df) == 0:
                self.error.emit("Не удалось обработать файлы или данные пусты")
                return

            # Маппинг уже выполнен в сервисе, df уже готов для Битрикс
            self.progress.emit(80, "Подготовка данных завершена...")

            # Замер времени окончания
            processing_time_ms = int((time.time() - start_time) * 1000)
            stats["processing_time_ms"] = processing_time_ms

            self.progress.emit(100, f"Обработка завершена: {len(df)} лидов")

            # Испускаем сигнал завершения
            self.finished.emit(df, stats)

        except Exception as e:
            error_message = f"Ошибка обработки: {str(e)}"
            self.error.emit(error_message)


class ExportThread(QThread):
    """
    Поток для экспорта данных в CSV.

    Запускает экспорт обработанных лидов в формат Битрикс24
    в отдельном потоке чтобы не блокировать GUI.

    Signals:
        finished: Экспорт завершён (bool, str)
        error: Произошла ошибка (str)

    Example:
        >>> thread = ExportThread(df, "/path/to/output.csv")
        >>> thread.finished.connect(lambda success, msg: print(msg))
        >>> thread.start()
    """

    # Сигналы
    finished = Signal(bool, str)  # Успех, сообщение
    error = Signal(str)  # Сообщение об ошибке

    def __init__(
        self,
        df,
        filepath: str,
        stage: str = "Новая заявка",
        source: str = "Холодный звонок",
        service_type: str = "ГЦК",
        parent: QThread | None = None,
    ) -> None:
        """
        Инициализация потока экспорта.

        Args:
            df: DataFrame с данными для экспорта
            filepath: Путь для сохранения файла
            stage: Стадия лида для Битрикс
            source: Источник лида
            service_type: Тип услуги
            parent: Родительский объект
        """
        super().__init__(parent)
        self._df = df
        self._filepath = filepath
        self._stage = stage
        self._source = source
        self._service_type = service_type

    def run(self) -> None:
        """
        Запуск экспорта в CSV.

        Выполняет:
        1. Маппинг данных (если нужно)
        2. Экспорт в CSV с разделителем ;
        3. Кодировка UTF-8 с BOM для Excel
        """
        try:
            # Экспорт в CSV
            success = export_to_bitrix_csv(
                self._df,
                self._filepath,
                stage=self._stage,
                source=self._source,
                service_type=self._service_type,
            )

            if success:
                leads_count = len(self._df)
                self.finished.emit(
                    True,
                    f"Файл успешно сохранён:\n{self._filepath}\n\nКоличество лидов: {leads_count}",
                )
            else:
                self.finished.emit(
                    False,
                    "Не удалось экспортировать файл.\nПроверьте путь и права доступа.",
                )

        except Exception as e:
            error_message = f"Ошибка экспорта: {str(e)}"
            self.error.emit(error_message)
