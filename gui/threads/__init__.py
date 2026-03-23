"""
Модуль потоков для GUI приложения.

Предоставляет QThread компоненты для фоновой обработки
и экспорта данных без блокировки интерфейса.

Classes:
    ProcessingThread: Обработка лидов (очистка, маппинг, распределение)
    ExportThread: Экспорт в Битрикс CSV

Example:
    >>> from gui.threads import ProcessingThread, ExportThread
    >>> thread = ProcessingThread(files, managers)
    >>> thread.start()
"""

from .processing_thread import ProcessingThread, ExportThread

__all__ = [
    "ProcessingThread",
    "ExportThread",
]
