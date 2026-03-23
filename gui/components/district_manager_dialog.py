"""
Диалог управления городами и районами для генератора ссылок.

Модуль предоставляет виджет DistrictManagerDialog для управления
списком городов и районов через удобный интерфейс.

Classes:
    DistrictManagerDialog: QDialog для управления городами и районами.

Example:
    >>> dialog = DistrictManagerDialog(parent)
    >>> if dialog.exec() == QDialog.Accepted:
    ...     config = dialog.get_updated_config()
"""

import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QMessageBox,
    QWidget,
)

from gui.styles.theme import (
    ACCENT_CYAN,
    ACCENT_CYAN_HOVER,
    BACKGROUND_PRIMARY,
    BACKGROUND_SECONDARY,
    BACKGROUND_TERTIARY,
    BORDER_COLOR,
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    STATUS_SUCCESS,
    STATUS_ERROR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
    GLASS_HOVER,
)
from utils.config_loader import load_config, save_config
from utils.url_generator import load_regions_from_config, load_city_districts
from utils.city_timezones import get_city_timezone, add_custom_timezone

logger = logging.getLogger(__name__)


class DistrictManagerDialog(QDialog):
    """
    Диалог управления городами и районами.

    Предоставляет интерфейс для:
    - Добавления/удаления городов
    - Добавления/удаления районов для городов
    - Просмотра списка всех городов и районов

    Example:
        >>> dialog = DistrictManagerDialog(parent)
        >>> if dialog.exec() == QDialog.Accepted:
        ...     config = dialog.get_updated_config()
        >>>     save_config(config)
    """

    def __init__(self, parent=None) -> None:
        """
        Инициализация диалога.

        Args:
            parent: Родительский виджет. По умолчанию None.
        """
        super().__init__(parent)
        self.setObjectName("DistrictManagerDialog")
        self.setWindowTitle("Управление городами и районами")
        self.setMinimumSize(800, 600)

        # Загрузка конфигурации
        self._config = load_config()
        self._cities = load_regions_from_config(self._config)
        self._city_districts = load_city_districts(self._config)

        # Выбранный город для редактирования районов
        self._selected_city: str | None = None

        self._init_ui()
        self._apply_styles()
        self._connect_signals()
        self._populate_cities_list()

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Управление городами и районами")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # Основная область с двумя колонками
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        main_layout = QGridLayout(main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Левая колонка: Города
        left_widget = self._create_cities_panel()
        main_layout.addWidget(left_widget, 0, 0)

        # Правая колонка: Районы
        right_widget = self._create_districts_panel()
        main_layout.addWidget(right_widget, 0, 1)

        layout.addWidget(main_frame, stretch=1)

        # Кнопки управления (Закрыть)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        buttons_layout.addStretch()

        # Кнопки OK/Cancel
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self._button_box)

        layout.addLayout(buttons_layout)

    def _create_cities_panel(self) -> QWidget:
        """
        Создание панели управления городами.

        Returns:
            QWidget с списком городов и кнопками управления.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("Города")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        # Список городов
        self._cities_list = QListWidget()
        self._cities_list.setObjectName("citiesList")
        self._cities_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._cities_list.itemSelectionChanged.connect(self._on_city_selection_changed)
        layout.addWidget(self._cities_list, stretch=1)

        # Кнопки управления городами
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self._add_city_btn = QPushButton("➕ Добавить")
        self._add_city_btn.setObjectName("minimalButton")
        buttons_layout.addWidget(self._add_city_btn)

        self._delete_cities_btn = QPushButton("🗑 Удалить выбранные")
        self._delete_cities_btn.setObjectName("dangerButton")
        buttons_layout.addWidget(self._delete_cities_btn)

        layout.addLayout(buttons_layout)

        # Статус
        self._cities_status = QLabel("")
        self._cities_status.setObjectName("statusLabel")
        layout.addWidget(self._cities_status)

        return widget

    def _create_districts_panel(self) -> QWidget:
        """
        Создание панели управления районами.

        Returns:
            QWidget с списком районов и кнопками управления.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("Районы")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        # Подсказка
        hint = QLabel("Выберите город для редактирования районов")
        hint.setObjectName("hintLabel")
        layout.addWidget(hint)

        # Название выбранного города
        self._selected_city_label = QLabel("")
        self._selected_city_label.setObjectName("selectedCityLabel")
        layout.addWidget(self._selected_city_label)

        # Список районов
        self._districts_list = QListWidget()
        self._districts_list.setObjectName("districtsList")
        self._districts_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._districts_list.setEnabled(False)
        layout.addWidget(self._districts_list, stretch=1)

        # Кнопки управления районами
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self._add_district_btn = QPushButton("➕ Добавить")
        self._add_district_btn.setObjectName("minimalButton")
        self._add_district_btn.setEnabled(False)
        buttons_layout.addWidget(self._add_district_btn)

        self._delete_districts_btn = QPushButton("🗑 Удалить выбранные")
        self._delete_districts_btn.setObjectName("dangerButton")
        self._delete_districts_btn.setEnabled(False)
        buttons_layout.addWidget(self._delete_districts_btn)

        layout.addLayout(buttons_layout)

        # Статус
        self._districts_status = QLabel("")
        self._districts_status.setObjectName("statusLabel")
        layout.addWidget(self._districts_status)

        return widget

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._add_city_btn.clicked.connect(self._add_city)
        self._delete_cities_btn.clicked.connect(self._delete_selected_cities)
        self._add_district_btn.clicked.connect(self._add_district)
        self._delete_districts_btn.clicked.connect(self._delete_selected_districts)

    def _apply_styles(self) -> None:
        """Применение стилей оформления."""
        self.setStyleSheet(f"""
            QDialog#DistrictManagerDialog {{
                background-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Заголовок диалога
        self.findChild(QLabel, "dialogTitle").setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: {FONT_SIZE_TITLE}px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)

        # Заголовки панелей
        for label in self.findChildren(QLabel, "panelTitle"):
            label.setStyleSheet(f"""
                QLabel {{
                    color: {ACCENT_CYAN};
                    font-size: {FONT_SIZE_TITLE}px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Подсказки
        for label in self.findChildren(QLabel, "hintLabel"):
            label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: {FONT_SIZE_SMALL}px;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Метка выбранного города
        self._selected_city_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: {FONT_SIZE_BODY}px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                padding: 8px 0;
            }}
        """)

        # Списки
        for list_widget in [self._cities_list, self._districts_list]:
            list_widget.setStyleSheet(f"""
                QListWidget {{
                    background-color: {BACKGROUND_TERTIARY};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 8px;
                    padding: 8px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QListWidget::item {{
                    padding: 8px;
                    border-radius: 4px;
                    margin: 2px 0;
                }}
                QListWidget::item:selected {{
                    background-color: {ACCENT_CYAN};
                    color: {BACKGROUND_PRIMARY};
                }}
                QListWidget::item:hover {{
                    background-color: {GLASS_HOVER};
                }}
            """)

        # Кнопки
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == "accentButton":
                btn.setStyleSheet(f"""
                    QPushButton#accentButton {{
                        background-color: {GLASS_BUTTON_BG};
                        color: {BACKGROUND_PRIMARY};
                        border: 1px solid rgba(6, 182, 212, 100);
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#accentButton:hover {{
                        background-color: rgba(6, 182, 212, 220);
                    }}
                """)
            elif btn.objectName() == "minimalButton":
                btn.setStyleSheet(f"""
                    QPushButton#minimalButton {{
                        background-color: rgba(255, 255, 255, 10);
                        color: {TEXT_PRIMARY};
                        border: 1px solid {GLASS_BORDER};
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#minimalButton:hover {{
                        background-color: {GLASS_HOVER};
                        border: 1px solid rgba(255, 255, 255, 40);
                        color: {ACCENT_CYAN};
                    }}
                    QPushButton#minimalButton:disabled {{
                        opacity: 0.5;
                    }}
                """)
            elif btn.objectName() == "dangerButton":
                btn.setStyleSheet(f"""
                    QPushButton#dangerButton {{
                        background-color: rgba(220, 38, 38, 150);
                        color: {BACKGROUND_PRIMARY};
                        border: 1px solid rgba(220, 38, 38, 100);
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#dangerButton:hover {{
                        background-color: rgba(220, 38, 38, 200);
                        border: 1px solid rgba(220, 38, 38, 150);
                    }}
                    QPushButton#dangerButton:disabled {{
                        opacity: 0.5;
                    }}
                """)

        # Статус
        for label in [self._cities_status, self._districts_status]:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: {FONT_SIZE_SMALL}px;
                    font-family: {FONT_FAMILY};
                    padding: 4px 0;
                }}
            """)

    def _populate_cities_list(self) -> None:
        """Заполнение списка городов."""
        self._cities_list.clear()
        for city in sorted(self._cities):
            timezone = get_city_timezone(city)
            item_text = f"{city}"
            if timezone:
                item_text += f" ({timezone})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, city)
            self._cities_list.addItem(item)

        self._cities_status.setText(f"Всего городов: {len(self._cities)}")

    def _on_city_selection_changed(self) -> None:
        """Обработчик выбора города."""
        selected_items = self._cities_list.selectedItems()

        if len(selected_items) == 1:
            city = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self._selected_city = city
            self._selected_city_label.setText(f"Город: {city}")
            self._populate_districts_list(city)
            self._add_district_btn.setEnabled(True)
            self._delete_districts_btn.setEnabled(True)
            self._districts_list.setEnabled(True)
        elif len(selected_items) > 1:
            self._selected_city = None
            self._selected_city_label.setText(f"Выбрано городов: {len(selected_items)}")
            self._districts_list.clear()
            self._districts_list.setEnabled(False)
            self._add_district_btn.setEnabled(False)
            self._delete_districts_btn.setEnabled(False)
        else:
            self._selected_city = None
            self._selected_city_label.setText("")
            self._districts_list.clear()
            self._districts_list.setEnabled(False)
            self._add_district_btn.setEnabled(False)
            self._delete_districts_btn.setEnabled(False)

    def _populate_districts_list(self, city: str) -> None:
        """
        Заполнение списка районов для города.

        Args:
            city: Название города
        """
        self._districts_list.clear()
        districts = self._city_districts.get(city, [])

        for district in sorted(districts):
            item = QListWidgetItem(district)
            item.setData(Qt.ItemDataRole.UserRole, district)
            self._districts_list.addItem(item)

        self._districts_status.setText(f"Всего районов: {len(districts)}")

    def _add_city(self) -> None:
        """Добавление нового города с обязательным вводом часового пояса."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить город")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Поле "Город"
        city_label = QLabel("Название города:")
        layout.addWidget(city_label)
        city_input = QLineEdit()
        city_input.setPlaceholderText("Например: Владивосток")
        layout.addWidget(city_input)

        # Поле "Часовой пояс" (обязательно)
        tz_label = QLabel("Часовой пояс (UTC+X) *обязательно:")
        layout.addWidget(tz_label)
        timezone_input = QLineEdit()
        timezone_input.setPlaceholderText("Например: UTC+10")
        layout.addWidget(timezone_input)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            city = city_input.text().strip()
            timezone = timezone_input.text().strip()

            if not city:
                self._cities_status.setText("❌ Введите название города")
                self._cities_status.setStyleSheet(f"color: {STATUS_ERROR};")
                return

            if not timezone:
                self._cities_status.setText("❌ Введите часовой пояс")
                self._cities_status.setStyleSheet(f"color: {STATUS_ERROR};")
                return

            if city in self._cities:
                self._cities_status.setText(f"⚠️ Город '{city}' уже существует")
                self._cities_status.setStyleSheet(f"color: orange;")
                return

            # Добавляем город
            self._cities.append(city)
            self._config["regions"] = self._cities

            # Сохраняем часовой пояс
            add_custom_timezone(city, timezone)

            # Сохраняем конфигурацию
            if save_config(self._config):
                self._populate_cities_list()
                self._cities_status.setText(f"✅ Город '{city}' добавлен")
                self._cities_status.setStyleSheet(f"color: {STATUS_SUCCESS};")
                logger.info(f"Добавлен город с поясом: {city} ({timezone})")
            else:
                self._cities_status.setText(f"❌ Ошибка сохранения")
                self._cities_status.setStyleSheet(f"color: {STATUS_ERROR};")
                logger.error(f"Ошибка сохранения города: {city}")

    def _delete_selected_cities(self) -> None:
        """
        Удаление выбранных городов.

        Запрашивает подтверждение перед удалением.
        """
        selected_items = self._cities_list.selectedItems()

        if not selected_items:
            self._cities_status.setText("❌ Выберите города для удаления")
            self._cities_status.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        cities_to_delete = [
            item.data(Qt.ItemDataRole.UserRole) for item in selected_items
        ]
        cities_text = ", ".join(cities_to_delete[:5])
        if len(cities_to_delete) > 5:
            cities_text += f" и ещё {len(cities_to_delete) - 5}"

        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить города:\n{cities_text}?\n\n"
            f"Районы этих городов также будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Удаляем города
        for city in cities_to_delete:
            if city in self._cities:
                self._cities.remove(city)

            # Удаляем районы
            if city in self._city_districts:
                del self._city_districts[city]

        # Обновляем конфигурацию
        self._config["regions"] = self._cities
        self._config["city_districts"] = self._city_districts

        if save_config(self._config):
            self._populate_cities_list()
            self._selected_city = None
            self._selected_city_label.setText("")
            self._districts_list.clear()
            self._cities_status.setText(f"✅ Удалено городов: {len(cities_to_delete)}")
            self._cities_status.setStyleSheet(f"color: {STATUS_SUCCESS};")
            logger.info(f"Удалены города: {cities_to_delete}")
        else:
            self._cities_status.setText(f"❌ Ошибка сохранения")
            self._cities_status.setStyleSheet(f"color: {STATUS_ERROR};")
            logger.error(f"Ошибка удаления городов: {cities_to_delete}")

    def _add_district(self) -> None:
        """Добавление района для выбранного города."""
        if not self._selected_city:
            self._districts_status.setText("❌ Выберите город")
            self._districts_status.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        from PySide6.QtWidgets import QInputDialog

        district, ok = QInputDialog.getText(
            self,
            "Добавить район",
            f"Введите название района для города '{self._selected_city}':",
            text="",
        )

        if ok and district.strip():
            district = district.strip()

            # Инициализируем список районов если нет
            if self._selected_city not in self._city_districts:
                self._city_districts[self._selected_city] = []

            if district in self._city_districts[self._selected_city]:
                self._districts_status.setText(
                    f"⚠️ Район '{district}' уже существует"
                )
                self._districts_status.setStyleSheet(f"color: orange;")
                return

            self._city_districts[self._selected_city].append(district)
            self._config["city_districts"] = self._city_districts

            if save_config(self._config):
                self._populate_districts_list(self._selected_city)
                self._districts_status.setText(f"✅ Район '{district}' добавлен")
                self._districts_status.setStyleSheet(f"color: {STATUS_SUCCESS};")
                logger.info(
                    f"Добавлен район: {district} для города {self._selected_city}"
                )
            else:
                self._districts_status.setText(f"❌ Ошибка сохранения")
                self._districts_status.setStyleSheet(f"color: {STATUS_ERROR};")
                logger.error(
                    f"Ошибка сохранения района: {district} для {self._selected_city}"
                )

    def _delete_selected_districts(self) -> None:
        """
        Удаление выбранных районов.

        Запрашивает подтверждение перед удалением.
        """
        if not self._selected_city:
            self._districts_status.setText("❌ Выберите город")
            self._districts_status.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        selected_items = self._districts_list.selectedItems()

        if not selected_items:
            self._districts_status.setText("❌ Выберите районы для удаления")
            self._districts_status.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        districts_to_delete = [
            item.data(Qt.ItemDataRole.UserRole) for item in selected_items
        ]
        districts_text = ", ".join(districts_to_delete[:5])
        if len(districts_to_delete) > 5:
            districts_text += f" и ещё {len(districts_to_delete) - 5}"

        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить районы:\n{districts_text}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Удаляем районы
        for district in districts_to_delete:
            if district in self._city_districts.get(self._selected_city, []):
                self._city_districts[self._selected_city].remove(district)

        # Очищаем пустой список районов
        if not self._city_districts.get(self._selected_city, []):
            del self._city_districts[self._selected_city]

        self._config["city_districts"] = self._city_districts

        if save_config(self._config):
            self._populate_districts_list(self._selected_city)
            self._districts_status.setText(
                f"✅ Удалено районов: {len(districts_to_delete)}"
            )
            self._districts_status.setStyleSheet(f"color: {STATUS_SUCCESS};")
            logger.info(
                f"Удалены районы: {districts_to_delete} для города {self._selected_city}"
            )
        else:
            self._districts_status.setText(f"❌ Ошибка сохранения")
            self._districts_status.setStyleSheet(f"color: {STATUS_ERROR};")
            logger.error(
                f"Ошибка удаления районов: {districts_to_delete} для {self._selected_city}"
            )

    def get_updated_config(self) -> dict:
        """
        Получение обновлённой конфигурации.

        Returns:
            Словарь конфигурации с изменениями
        """
        return self._config
