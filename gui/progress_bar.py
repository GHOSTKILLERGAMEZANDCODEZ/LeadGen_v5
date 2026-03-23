"""
Виджет прогресс-бара для PySide6.

Обёртка над QProgressBar с текстовыми подписями состояния.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt


class ProgressWidget(QWidget):
    """
    Виджет с прогресс-баром и текстовой подписью.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Инициализирует UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # Текст состояния
        self.status_label = QLabel("Ожидание...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        layout.addWidget(self.status_label)

    def set_progress(self, value: int) -> None:
        """
        Устанавливает значение прогресса.

        Args:
            value: Значение от 0 до 100
        """
        self.progress_bar.setValue(value)

    def set_status(self, text: str) -> None:
        """
        Устанавливает текст состояния.

        Args:
            text: Текст статуса
        """
        self.status_label.setText(text)

    def reset(self) -> None:
        """Сбрасывает прогресс в начальное состояние."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Ожидание...")

    def set_range(self, minimum: int, maximum: int) -> None:
        """
        Устанавливает диапазон прогресс-бара.

        Args:
            minimum: Минимальное значение
            maximum: Максимальное значение
        """
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)

    def set_indeterminate(self, indeterminate: bool = True) -> None:
        """
        Включает/выключает неопределённый режим (анимация).

        Args:
            indeterminate: True для включения режима
        """
        if indeterminate:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
