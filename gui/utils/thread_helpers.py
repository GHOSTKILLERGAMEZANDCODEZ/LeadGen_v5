"""
Утилиты для работы с потоками в PySide6.

Предоставляет базовые классы и декораторы для безопасной работы с QThread.
"""

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QCloseEvent
import logging

logger = logging.getLogger(__name__)
THREAD_STOP_TIMEOUT_MS = 3000


class ThreadCleanupMixin:
    """
    Миксин для автоматической очистки QThread при закрытии виджета.
    
    Example:
        class ProcessingPage(ThreadCleanupMixin, QWidget):
            def __init__(self):
                super().__init__()
                self._processing_thread: QThread | None = None
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threads: list[QThread] = []
    
    def register_thread(self, thread: QThread) -> None:
        """
        Зарегистрировать поток для автоматической очистки.
        
        Args:
            thread: Поток для регистрации
        """
        if thread not in self._threads:
            self._threads.append(thread)

    def _stop_thread(self, thread: QThread) -> None:
        """Останавливает поток с принудительным завершением при необходимости."""
        if not thread or not thread.isRunning():
            return
        
        logger.debug("Stopping thread: %s", thread)
        thread.quit()
        
        if not thread.wait(THREAD_STOP_TIMEOUT_MS):
            logger.warning("Thread %s did not finish gracefully, forcing terminate", thread)
            thread.terminate()
            
            if not thread.wait(1000):
                logger.error("Thread %s could not be terminated!", thread)
    
    def unregister_thread(self, thread: QThread) -> None:
        """
        Отменить регистрацию потока.
        
        Args:
            thread: Поток для отмены регистрации
        """
        if thread in self._threads:
            self._threads.remove(thread)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Очистка всех зарегистрированных потоков при закрытии.
        
        Args:
            event: Событие закрытия
        """
        for thread in self._threads:
            self._stop_thread(thread)
        
        self._threads.clear()
        handler = getattr(super(), "closeEvent", None)
        if handler:
            handler(event)
