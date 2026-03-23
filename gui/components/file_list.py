"""
Виджет списка файлов с кнопками управления.

Модуль предоставляет виджет FileListWidget для отображения и управления
списком загруженных файлов с поддержкой удаления отдельных элементов
и полной очистки списка.

Classes:
    FileListWidget: QWidget для отображения списка файлов с кнопками управления.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.styles.theme import FONT_SIZE_SMALL, FONT_SIZE_TITLE, TEXT_PRIMARY, TEXT_SECONDARY


class FileListWidget(QWidget):
    """
    Виджет списка файлов с кнопками управления.

    Позволяет отображать список загруженных файлов, удалять выбранные
    элементы и очищать весь список. Поддерживает double click для удаления
    и автоматическое обновление счётчика файлов.

    Attributes:
        files_changed: Сигнал, испускаемый при изменении списка файлов.
            Передаёт список путей к файлам.
        remove_selected: Сигнал, испускаемый при удалении выбранного файла.
        clear_all: Сигнал, испускаемый при очистке всего списка.

    Example:
        >>> widget = FileListWidget()
        >>> widget.files_changed.connect(lambda paths: print(f"Files: {paths}"))
        >>> widget.add_files(["file1.json", "file2.tsv"])
        >>> widget.show()
    """

    # Сигналы
    files_changed = Signal(list)
    remove_selected = Signal()
    clear_all = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Инициализация виджета списка файлов.

        Args:
            parent: Родительский виджет. По умолчанию None.
        """
        super().__init__(parent)
        self._file_paths: list[str] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Инициализация пользовательского интерфейса.

        Создаёт и настраивает все элементы виджета:
        - Заголовок "Загруженные файлы" (16px, bold)
        - QListWidget для отображения файлов
        - Кнопки "Удалить выбранное" и "Очистить всё" (minimalButton)
        - Счётчик "N файлов" (11px, secondary)

        Применяет стилизацию с использованием констант из theme.py.
        """
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Заголовок
        self._title_label = QLabel("Загруженные файлы")
        self._title_label.setStyleSheet(
            f"font-size: {FONT_SIZE_TITLE}px;"
            f"font-weight: bold;"
            f"color: {TEXT_PRIMARY};"
        )
        main_layout.addWidget(self._title_label)

        # Список файлов (прозрачный)
        self._list_widget = QListWidget()
        self._list_widget.setStyleSheet(
            f"background-color: rgba(30, 30, 30, 60);"
            f"border: 1px solid rgba(255, 255, 255, 30);"
            f"border-radius: 8px;"
            f"color: {TEXT_PRIMARY};"
            f"outline: none;"
            f"QListWidget::item {{ padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 20); }}"
            f"QListWidget::item:selected {{ background-color: rgba(6, 182, 212, 120); color: {TEXT_PRIMARY}; }}"
            f"QListWidget::item:hover {{ border: 1px solid rgba(255, 255, 255, 40); }}"
        )
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self._list_widget.itemDoubleClicked.connect(self._remove_selected_item)
        main_layout.addWidget(self._list_widget)

        # Layout для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Кнопка "Удалить выбранное"
        self._remove_button = QPushButton("Удалить выбранное")
        self._remove_button.setObjectName("minimalButton")
        self._remove_button.clicked.connect(self._remove_selected)
        self._remove_button.setEnabled(False)
        buttons_layout.addWidget(self._remove_button)

        # Кнопка "Очистить всё"
        self._clear_button = QPushButton("Очистить всё")
        self._clear_button.setObjectName("minimalButton")
        self._clear_button.clicked.connect(self._clear_all_files)
        self._clear_button.setEnabled(False)
        buttons_layout.addWidget(self._clear_button)

        main_layout.addLayout(buttons_layout)

        # Счётчик
        self._count_label = QLabel("0 файлов")
        self._count_label.setStyleSheet(
            f"font-size: {FONT_SIZE_SMALL}px;" f"color: {TEXT_SECONDARY};"
        )
        main_layout.addWidget(self._count_label)

    def _on_selection_changed(self) -> None:
        """
        Обработка изменения выделения в списке.

        Включает кнопку "Удалить выбранное" если есть выбранные элементы,
        иначе отключает её.
        """
        has_selection = len(self._list_widget.selectedItems()) > 0
        self._remove_button.setEnabled(has_selection)

    def _remove_selected_item(self, item: QListWidgetItem | None = None) -> None:
        """
        Удаление выбранного элемента из списка.

        Args:
            item: Элемент для удаления. Если None, удаляется текущий выбранный.
        """
        if item is None:
            selected_items = self._list_widget.selectedItems()
            if not selected_items:
                return
            item = selected_items[0]

        row = self._list_widget.row(item)
        if 0 <= row < len(self._file_paths):
            self._file_paths.pop(row)
            self._list_widget.takeItem(row)
            self._emit_changes()
            self.remove_selected.emit()

    def _remove_selected(self) -> None:
        """
        Удаление выбранного файла по кнопке.

        Вызывает _remove_selected_item для текущего выбранного элемента.
        """
        self._remove_selected_item()

    def _clear_all_files(self) -> None:
        """
        Очистка всего списка файлов.

        Удаляет все элементы из списка и сбрасывает внутренние данные.
        """
        self._file_paths.clear()
        self._list_widget.clear()
        self._remove_button.setEnabled(False)
        self._emit_changes()
        self.clear_all.emit()

    def _update_count(self) -> None:
        """
        Обновление счётчика файлов.

        Устанавливает текст счётчика в формате "N файлов" и управляет
        доступностью кнопки "Очистить всё".
        """
        count = len(self._file_paths)
        self._count_label.setText(f"{count} файлов")
        self._clear_button.setEnabled(count > 0)

    def _emit_changes(self) -> None:
        """
        Обновление счётчика и уведомление об изменениях.
        """
        self._update_count()
        self.files_changed.emit(self._file_paths)

    def add_files(self, file_paths: list[str]) -> None:
        """
        Добавление файлов в список.

        Args:
            file_paths: Список путей к файлам для добавления.

        Note:
            Дубликаты файлов не добавляются.
        """
        for path in file_paths:
            if path not in self._file_paths:
                self._file_paths.append(path)
                item = QListWidgetItem(path)
                item.setToolTip(path)
                self._list_widget.addItem(item)

        self._emit_changes()

    def get_file_paths(self) -> list[str]:
        """
        Получение списка путей к файлам.

        Returns:
            Список путей к текущим файлам в виджете.
        """
        return self._file_paths.copy()
