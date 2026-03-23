"""
Виджет загрузки файлов с поддержкой Drag&Drop.

Модуль предоставляет виджет FileLoaderWidget для загрузки файлов
через перетаскивание или клик. Поддерживает форматы JSON, TSV, CSV.

Classes:
    FileLoaderWidget: QWidget с поддержкой Drag&Drop для загрузки файлов.
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import QFileDialog, QLabel, QVBoxLayout, QWidget

from gui.styles.theme import (
    ACCENT_CYAN,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class FileLoaderWidget(QWidget):
    """
    Виджет загрузки файлов с поддержкой Drag&Drop.

    Позволяет пользователю загружать файлы через перетаскивание
    из проводника или клик для выбора файлов. Поддерживает форматы
    JSON, TSV, CSV.

    Attributes:
        files_selected: Сигнал, испускаемый при выборе файлов.
            Передаёт список путей к выбранным файлам.

    Example:
        >>> widget = FileLoaderWidget()
        >>> widget.files_selected.connect(lambda paths: print(f"Selected: {paths}"))
        >>> widget.show()
    """

    # Сигнал с списком путей к выбранным файлам
    files_selected = Signal(list)

    # Поддерживаемые расширения файлов
    SUPPORTED_EXTENSIONS = {".json", ".tsv", ".csv"}
    FILE_FILTER = "Файлы данных (*.json *.tsv *.csv);;Все файлы (*.*)"

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Инициализация виджета загрузки файлов.

        Args:
            parent: Родительский виджет. По умолчанию None.
        """
        super().__init__(parent)
        self._drag_entered = False
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Инициализация пользовательского интерфейса.

        Создаёт и настраивает все элементы виджета:
        - Layout с отступами 24px по бокам, 32px сверху/снизу
        - Иконка папки (48px)
        - Заголовок (16px, bold)
        - Описание (11px, secondary)

        Применяет стилизацию с использованием констант из theme.py.
        """
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Иконка
        self._icon_label = QLabel("📁")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet(f"font-size: 48px;")
        layout.addWidget(self._icon_label)

        # Заголовок
        self._title_label = QLabel("Перетащите файлы сюда")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet(
            f"font-size: {FONT_SIZE_TITLE}px;"
            f"font-weight: bold;"
            f"color: {TEXT_PRIMARY};"
        )
        layout.addWidget(self._title_label)

        # Описание
        self._description_label = QLabel("или нажмите для выбора (JSON, TSV, CSV)")
        self._description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description_label.setStyleSheet(
            f"font-size: {FONT_SIZE_SMALL}px;" f"color: {TEXT_SECONDARY};"
        )
        layout.addWidget(self._description_label)

        # Применение начального стиля
        self._apply_normal_style()

        # Включение Drag&Drop
        self.setAcceptDrops(True)

    def _apply_normal_style(self) -> None:
        """
        Применение обычного стиля виджета.

        Устанавливает стандартное оформление с фоновым цветом,
        границей и скруглением углов.
        """
        self.setStyleSheet(
            f"background-color: rgba(30, 30, 30, 60);"
            f"border: 2px dashed rgba(255, 255, 255, 30);"
            f"border-radius: 12px;"
        )

    def _apply_hover_style(self) -> None:
        """
        Применение стиля при наведении.

        Изменяет цвет границы на акцентный cyan для визуальной
        обратной связи при наведении курсора.
        """
        self.setStyleSheet(
            f"background-color: rgba(30, 30, 30, 80);"
            f"border: 2px dashed {ACCENT_CYAN};"
            f"border-radius: 12px;"
        )

    def _apply_drag_enter_style(self) -> None:
        """
        Применение стиля при перетаскивании файла над виджетом.

        Устанавливает cyan фон для индикации готовности принять файл.
        """
        self.setStyleSheet(
            f"background-color: {ACCENT_CYAN};"
            f"border: 2px dashed {ACCENT_CYAN};"
            f"border-radius: 12px;"
        )

    def _on_click(self, event) -> None:
        """
        Обработка клика для выбора файлов через диалог.

        Открывает диалог выбора файлов с фильтром по поддерживаемым
        форматам (JSON, TSV, CSV). При выборе файлов испускает
        сигнал files_selected.

        Args:
            event: Событие клика (не используется, но требуется для совместимости).
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы",
            "",
            self.FILE_FILTER,
        )

        if file_paths:
            self.files_selected.emit(file_paths)

    def _is_valid_file(self, path: Path) -> bool:
        """
        Проверка файла на поддержку формата.

        Args:
            path: Путь к файлу для проверки.

        Returns:
            True если файл имеет поддерживаемое расширение, иначе False.
        """
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _collect_valid_paths(self, urls) -> list[str]:
        file_paths: list[str] = []
        for url in urls:
            path = Path(url.toLocalFile())
            if self._is_valid_file(path):
                file_paths.append(str(path))
        return file_paths

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Обработка события входа перетаскивания в область виджета.

        Принимает событие только если перетаскиваются файлы с
        поддерживаемыми расширениями. Изменяет стиль виджета
        для визуальной обратной связи.

        Args:
            event: Событие drag enter.
        """
        if event.mimeData().hasUrls():
            has_valid_files = bool(self._collect_valid_paths(event.mimeData().urls()))

            if has_valid_files:
                event.acceptProposedAction()
                self._drag_entered = True
                self._apply_drag_enter_style()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        """
        Обработка события выхода перетаскивания из области виджета.

        Восстанавливает обычный стиль виджета.

        Args:
            event: Событие drag leave.
        """
        self._drag_entered = False
        self._apply_normal_style()

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Обработка события сброса перетаскиваемых файлов.

        Извлекает пути к файлам из события, фильтрует по поддерживаемым
        форматам и испускает сигнал files_selected с списком путей.
        Восстанавливает обычный стиль виджета.

        Args:
            event: Событие drop.
        """
        self._drag_entered = False
        self._apply_normal_style()

        if event.mimeData().hasUrls():
            file_paths = self._collect_valid_paths(event.mimeData().urls())

            if file_paths:
                self.files_selected.emit(file_paths)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def enterEvent(self, event) -> None:
        """
        Обработка события входа курсора в область виджета.

        Изменяет стиль границы на акцентный для визуальной
        обратной связи при наведении.

        Args:
            event: Событие enter.
        """
        if not self._drag_entered:
            self._apply_hover_style()

    def leaveEvent(self, event) -> None:
        """
        Обработка события выхода курсора из области виджета.

        Восстанавливает обычный стиль виджета.

        Args:
            event: Событие leave.
        """
        if not self._drag_entered:
            self._apply_normal_style()

    def mousePressEvent(self, event) -> None:
        """
        Обработка события нажатия кнопки мыши.

        Запускает диалог выбора файлов при клике на виджет.

        Args:
            event: Событие нажатия мыши.
        """
        self._on_click(event)
