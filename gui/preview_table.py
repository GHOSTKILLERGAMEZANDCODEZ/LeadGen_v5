"""
Виджет таблицы для предпросмотра данных.

Использует QTableView для отображения DataFrame.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QLabel, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt
import pandas as pd


class DataFrameModel(QAbstractTableModel):
    """
    Модель для отображения pandas DataFrame в QTableView.
    """

    def __init__(self, dataframe: pd.DataFrame = None):
        super().__init__()
        self._dataframe = dataframe

    def setDataFrame(self, dataframe: pd.DataFrame) -> None:
        """
        Устанавливает DataFrame для отображения.

        Args:
            dataframe: DataFrame для отображения
        """
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()

    def rowCount(self, parent=None) -> int:
        """Возвращает количество строк."""
        if self._dataframe is None:
            return 0
        return len(self._dataframe)

    def columnCount(self, parent=None) -> int:
        """Возвращает количество колонок."""
        if self._dataframe is None:
            return 0
        return len(self._dataframe.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Возвращает данные для ячейки."""
        if self._dataframe is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            value = self._dataframe.iloc[index.row(), index.column()]
            if pd.isna(value):
                return ""
            return str(value)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Возвращает заголовки."""
        if self._dataframe is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._dataframe.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)

        return None


class PreviewTable(QWidget):
    """
    Виджет для предпросмотра данных в виде таблицы.

    Отображает все строки DataFrame без ограничений.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_theme = True  # Всегда тёмная тема
        self._init_ui()

    def _init_ui(self) -> None:
        """Инициализирует UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header_label = QLabel("Предпросмотр результатов")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(header_label)

        # Таблица
        self.table_view = QTableView()
        self.model = DataFrameModel()
        self.table_view.setModel(self.model)

        # Настройка таблицы
        self.table_view.setAlternatingRowColors(True)
        self._update_table_style()

        # Растягивание колонок
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        # Вертикальный заголовок (номера строк)
        vertical_header = self.table_view.verticalHeader()
        vertical_header.setVisible(True)

        layout.addWidget(self.table_view)

        # Статус с информацией о количестве строк
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "color: #808080; font-size: 12px; padding: 4px;"
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def _update_table_style(self) -> None:
        """Обновляет стиль таблицы под тему."""
        if self.is_dark_theme:
            self.table_view.setStyleSheet("""
                QTableView {
                    gridline-color: #3c3c3c;
                    background-color: #252526;
                    color: #d4d4d4;
                    alternate-background-color: #2d2d30;
                }
                QTableView::item {
                    padding: 6px;
                }
                QTableView::item:selected {
                    background-color: #0e639c;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #333333;
                    color: #d4d4d4;
                    border: none;
                    padding: 8px;
                }
            """)
        else:
            self.table_view.setStyleSheet("""
                QTableView {
                    gridline-color: #e0e0e0;
                    background-color: white;
                    color: #333333;
                    alternate-background-color: #f5f5f5;
                }
                QTableView::item {
                    padding: 6px;
                }
                QTableView::item:selected {
                    background-color: #1a73e8;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #5f6368;
                    border: none;
                    padding: 8px;
                }
            """)

    def set_dark_theme(self, is_dark: bool) -> None:
        """Устанавливает тёмную тему."""
        self.is_dark_theme = is_dark
        self._update_table_style()

    def set_data(self, df: pd.DataFrame, stats: dict | None = None) -> None:
        """
        Устанавливает данные для отображения.

        Отображает все строки DataFrame.

        Args:
            df: DataFrame с данными
            stats: Статистика обработки
        """
        self.model.setDataFrame(df)

        # Обновляем статус
        status_parts = []
        total = len(df)
        status_parts.append(f"Показано {total} строк")

        if stats:
            processed = stats.get("total_rows", 0) - stats.get("duplicates_removed", 0)
            unique_phones = processed
            duplicates = stats.get("duplicates_removed", 0)
            status_parts.append(
                f"Обработано: {processed} | Уникальных: {unique_phones} | Дубликатов удалено: {duplicates}"
            )

        self.status_label.setText(" | ".join(status_parts))

    def clear(self) -> None:
        """Очищает таблицу."""
        self.model.setDataFrame(pd.DataFrame())
        self.status_label.setText("")
