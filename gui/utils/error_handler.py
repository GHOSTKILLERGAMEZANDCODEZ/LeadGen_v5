"""
Декораторы для обработки ошибок в слотах PySide6.

Предоставляет декораторы для безопасной обработки исключений в slot methods.
"""

from functools import wraps
from collections.abc import Callable
from typing import Any
from PySide6.QtWidgets import QMessageBox, QWidget
import logging

logger = logging.getLogger(__name__)


def _wrap_slot(
    func: Callable, title: str = "Ошибка", show_message: bool = True
) -> Callable:
    @wraps(func)
    def wrapper(self: QWidget, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.exception("Slot error in %s: %s", func.__name__, e)
            if show_message:
                QMessageBox.critical(
                    self,
                    title,
                    f"Произошла ошибка:\n{str(e)}\n\nПодробности в логе.",
                )
    return wrapper
