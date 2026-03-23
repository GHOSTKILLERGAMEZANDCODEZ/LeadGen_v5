"""
Страница генератора ссылок для Яндекс.Карт.

Модуль предоставляет виджет LinkGeneratorPage для генерации
поисковых ссылок по запросам [Сегмент] + [Регион].

Classes:
    LinkGeneratorPage: QWidget для генерации ссылок Яндекс.Карт.

Example:
    >>> page = LinkGeneratorPage()
    >>> page.show()
"""

import csv

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
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
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
    GLASS_HOVER,
)
from utils.url_generator import (
    generate_links_batch,
    load_city_districts,
    load_regions_from_config,
    save_links_to_csv,
)
from utils.config_loader import load_config, save_config
from utils.city_timezones import get_city_timezone


class LinkGeneratorPage(QWidget):
    """
    Страница генератора ссылок для Яндекс.Карт.

    Виджет предоставляет интерфейс для генерации поисковых ссылок
    по запросам [Сегмент] + [Регион/Город].

    Signals:
        links_generated: Сигнал о генерации ссылок (количество)

    Example:
        >>> page = LinkGeneratorPage()
        >>> page.links_generated.connect(lambda count: print(f"Generated {count} links"))
        >>> page.show()
    """

    links_generated = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Инициализация страницы генератора ссылок.

        Args:
            parent: Родительский виджет. По умолчанию None.
        """
        super().__init__(parent)
        self.setObjectName("LinkGeneratorPage")

        # Загрузка конфигурации
        self._config = load_config()
        self._cities = load_regions_from_config(self._config)
        self._city_districts = load_city_districts(self._config)

        # Выбранные города (по умолчанию все)
        self._selected_cities: set[str] = set(self._cities)

        # Результаты генерации
        self._generated_links: list[dict] = []

        self._init_ui()
        self._apply_styles()
        self._connect_signals()

    def _init_ui(self) -> None:
        """
        Инициализация пользовательского интерфейса.

        Новая структура (горизонтальная компоновка с QSplitter):
        - Заголовок "Генератор ссылок для Яндекс.Карт" (20px, bold)
        - QSplitter: слева сегмент + результаты, справа города
        """
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # Заголовок страницы
        self._page_title = QLabel("Генератор ссылок для Яндекс.Карт")
        self._page_title.setObjectName("pageTitle")
        main_layout.addWidget(self._page_title)

        # QSplitter: левая часть (сегмент + результаты) и правая часть (города)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainSplitter")
        splitter.setHandleWidth(6)

        # Левая часть: Сегмент + Результаты
        left_widget = self._create_segment_and_result_panel()
        splitter.addWidget(left_widget)

        # Правая часть: Города
        right_widget = self._create_cities_panel()
        splitter.addWidget(right_widget)

        # Пропорции 50/50
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, stretch=1)

    def _create_segment_and_result_panel(self) -> QWidget:
        """
        Создание панели сегмента и результатов.

        Returns:
            QWidget с полем сегмента и результатами генерации.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Подсказка
        hint_label = QLabel(
            "Введите поисковый запрос (сегмент) для генерации ссылок"
        )
        hint_label.setObjectName("hintLabel")
        layout.addWidget(hint_label)

        # Поле ввода сегмента
        segment_layout = QVBoxLayout()
        segment_label = QLabel("Поисковый запрос (сегмент):")
        segment_label.setObjectName("segmentLabel")
        segment_layout.addWidget(segment_label)

        self._segment_input = QTextEdit()
        self._segment_input.setObjectName("segmentInput")
        self._segment_input.setPlaceholderText(
            "Например: Металлоконструкции, Строительные материалы, Автосервис"
        )
        self._segment_input.setMaximumHeight(80)
        segment_layout.addWidget(self._segment_input)

        layout.addLayout(segment_layout)

        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        self._generate_button = QPushButton("Сгенерировать ссылки")
        self._generate_button.setObjectName("accentButton")
        self._generate_button.setMinimumHeight(48)
        actions_layout.addWidget(self._generate_button)

        self._copy_button = QPushButton("Копировать")
        self._copy_button.setObjectName("minimalButton")
        self._copy_button.setEnabled(False)
        actions_layout.addWidget(self._copy_button)

        self._export_button = QPushButton("Экспорт CSV")
        self._export_button.setObjectName("minimalButton")
        self._export_button.setEnabled(False)
        actions_layout.addWidget(self._export_button)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Статус
        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

        # Результат (список ссылок)
        result_label = QLabel("Результаты:")
        result_label.setObjectName("resultTitle")
        layout.addWidget(result_label)

        self._result_input = QTextEdit()
        self._result_input.setObjectName("resultInput")
        self._result_input.setReadOnly(True)
        self._result_input.setPlaceholderText(
            "Здесь появятся сгенерированные ссылки..."
        )
        layout.addWidget(self._result_input)

        # Счётчик
        self._count_label = QLabel("0 ссылок")
        self._count_label.setObjectName("countLabel")
        layout.addWidget(self._count_label)

        return widget

    def _create_cities_panel(self) -> QWidget:
        """
        Создание панели городов.

        Returns:
            QWidget со списком городов и кнопками управления.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Заголовок и кнопки управления в одной строке (компактно)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        cities_title = QLabel("Города:")
        cities_title.setObjectName("citiesTitle")
        header_layout.addWidget(cities_title, stretch=1)

        # Кнопка управления городами и районами
        self._manage_districts_btn = QPushButton("⚙ Управление")
        self._manage_districts_btn.setObjectName("minimalButton")
        self._manage_districts_btn.setMinimumHeight(32)
        header_layout.addWidget(self._manage_districts_btn)

        # Кнопка удаления выбранных городов
        self._delete_selected_cities_btn = QPushButton("🗑 Удалить выбранные")
        self._delete_selected_cities_btn.setObjectName("dangerButton")
        self._delete_selected_cities_btn.setMinimumHeight(32)
        header_layout.addWidget(self._delete_selected_cities_btn)

        layout.addLayout(header_layout)

        # Чекбокс "Учитывать районы"
        self._districts_checkbox = QCheckBox(
            "Учитывать районы городов (Москва - ЦАО, СПб - Адмиралтейский и т.д.)"
        )
        self._districts_checkbox.setObjectName("districtsCheckbox")
        self._districts_checkbox.setChecked(False)
        self._districts_checkbox.stateChanged.connect(self._on_districts_toggled)
        layout.addWidget(self._districts_checkbox)

        # Скролл с чекбоксами городов
        self._cities_scroll = QScrollArea()
        self._cities_scroll.setObjectName("citiesScroll")
        self._cities_scroll.setWidgetResizable(True)
        self._cities_scroll.setMaximumHeight(300)

        # Контент скролла
        cities_content = QWidget()
        self._cities_layout = QGridLayout(cities_content)
        self._cities_layout.setSpacing(8)
        self._cities_layout.setContentsMargins(8, 8, 8, 8)

        # Создание чекбоксов
        self._city_checkboxes: dict[str, QCheckBox] = {}
        self._create_city_checkboxes()

        self._cities_scroll.setWidget(cities_content)
        layout.addWidget(self._cities_scroll)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self._select_all_button = QPushButton("Выбрать все")
        self._select_all_button.setObjectName("minimalButton")
        buttons_layout.addWidget(self._select_all_button)

        self._deselect_all_button = QPushButton("Снять все")
        self._deselect_all_button.setObjectName("minimalButton")
        buttons_layout.addWidget(self._deselect_all_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return widget

    def _create_city_checkboxes(self) -> None:
        """Создание чекбоксов для городов (с районами если включена опция)."""
        # Очистка существующих
        for i in reversed(range(self._cities_layout.count())):
            widget = self._cities_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self._city_checkboxes.clear()

        # Часовые пояса отображаются ВСЕГДА (встроенная функция)
        # Загрузка списка городов из config для отображения поясов
        self._cities = load_regions_from_config(self._config)

        # Создание чекбоксов (2 колонки)
        column = 0
        row = 0
        max_rows = 20

        for city in sorted(self._cities):
            # Формируем текст с часовым поясом (всегда показываем)
            timezone = get_city_timezone(city)
            if timezone:
                checkbox_text = f"{city} - {timezone}"
            else:
                checkbox_text = city

            checkbox = QCheckBox(checkbox_text)
            checkbox.setObjectName(f"city_{city}")
            checkbox.setChecked(city in self._selected_cities)
            checkbox.stateChanged.connect(
                lambda state, c=city: self._on_city_toggled(c, state)
            )

            self._city_checkboxes[city] = checkbox
            self._cities_layout.addWidget(checkbox, row, column)

            # Переход на следующую колонку/строку
            row += 1
            if row >= max_rows:
                row = 0
                column += 1

        # Добавление районов если чекбокс включён
        if self._districts_checkbox.isChecked():
            self._add_district_checkboxes()

    def _add_district_checkboxes(self) -> None:
        """Добавление чекбоксов районов для выбранных городов."""
        for city, districts in self._city_districts.items():
            if city in self._selected_cities:
                for district in districts:
                    checkbox = QCheckBox(f"{city} - {district}")
                    checkbox.setObjectName(f"district_{city}_{district}")
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)  # Районы только для информации
                    self._city_checkboxes[f"{city}_{district}"] = checkbox

                    row = self._cities_layout.rowCount()
                    self._cities_layout.addWidget(checkbox, row, 0)

    def _on_districts_toggled(self, state: int) -> None:
        """
        Обработчик переключения чекбокса районов.

        Показывает/скрывает районы для выбранных городов.

        Args:
            state: Состояние чекбокса (0=unchecked, 2=checked)
        """
        # Пересоздаём чекбоксы с районами или без
        self._create_city_checkboxes()

    def _on_city_toggled(self, city: str, state: int) -> None:
        """
        Обработчик переключения чекбокса города.

        Args:
            city: Название города
            state: Состояние чекбокса (0=unchecked, 2=checked)
        """
        if state == 2:  # Checked
            self._selected_cities.add(city)
            # Добавляем районы этого города
            if city in self._city_districts:
                for district in self._city_districts[city]:
                    checkbox_key = f"{city}_{district}"
                    if checkbox_key in self._city_checkboxes:
                        self._city_checkboxes[checkbox_key].setChecked(True)
        else:
            self._selected_cities.discard(city)
            # Снимаем районы этого города
            if city in self._city_districts:
                for district in self._city_districts[city]:
                    checkbox_key = f"{city}_{district}"
                    if checkbox_key in self._city_checkboxes:
                        self._city_checkboxes[checkbox_key].setChecked(False)

    def reload_cities(self, config: dict) -> None:
        """
        Перезагружает список городов из конфигурации.

        Вызывается при изменении настроек в SettingsPage.

        Args:
            config: Обновлённая конфигурация приложения
        """
        from utils.url_generator import load_regions_from_config, load_city_districts

        self._config = config
        self._cities = load_regions_from_config(config)
        self._city_districts = load_city_districts(config)

        # Сохраняем выбранные города (если они ещё существуют)
        old_selected = self._selected_cities.copy()
        self._selected_cities = set(self._cities)  # По умолчанию все выбраны

        # Восстанавливаем предыдущий выбор если города существуют
        for city in old_selected:
            if city in self._cities:
                self._selected_cities.add(city)

        # Пересоздаём чекбоксы
        self._create_city_checkboxes()

    def _select_all_cities(self) -> None:
        """Выбрать все города."""
        for checkbox in self._city_checkboxes.values():
            checkbox.setChecked(True)
        self._selected_cities = set(self._cities)

    def _deselect_all_cities(self) -> None:
        """Снять все города."""
        for checkbox in self._city_checkboxes.values():
            checkbox.setChecked(False)
        self._selected_cities.clear()

    def _delete_selected_cities(self) -> None:
        """
        Удаление выбранных городов.

        Запрашивает подтверждение перед удалением.
        """
        if not self._selected_cities:
            self._status_label.setText("❌ Выберите города для удаления")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        cities_to_delete = list(self._selected_cities)
        cities_text = ", ".join(cities_to_delete[:5])
        if len(cities_to_delete) > 5:
            cities_text += f" и ещё {len(cities_to_delete) - 5}"

        # Подтверждение удаления
        from PySide6.QtWidgets import QMessageBox
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

        # Удаляем города из списка
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
            # Очищаем выбор
            self._selected_cities.clear()

            # Пересоздаём чекбоксы
            self._create_city_checkboxes()

            self._status_label.setText(f"✅ Удалено городов: {len(cities_to_delete)}")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
        else:
            self._status_label.setText(f"❌ Ошибка сохранения")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _open_district_manager(self) -> None:
        """
        Открытие диалога управления городами и районами.
        """
        from gui.components.district_manager_dialog import DistrictManagerDialog

        dialog = DistrictManagerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Обновляем конфигурацию после закрытия диалога
            self._config = load_config()
            self._cities = load_regions_from_config(self._config)
            self._city_districts = load_city_districts(self._config)

            # Пересоздаём чекбоксы
            self._create_city_checkboxes()

            self._status_label.setText("✅ Города и районы обновлены")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")

    def _get_selected_regions(self) -> list[str]:
        """
        Получение списка выбранных регионов.

        Returns:
            Список выбранных городов и районов (если чекбокс районов включён).
        """
        regions = list(self._selected_cities)

        # Добавляем районы если чекбокс включён
        if self._districts_checkbox.isChecked():
            for city, districts in self._city_districts.items():
                if city in self._selected_cities:
                    for district in districts:
                        regions.append(f"{city} - {district}")

        return regions

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._generate_button.clicked.connect(self._generate_links)
        self._copy_button.clicked.connect(self._copy_links)
        self._export_button.clicked.connect(self._export_links)
        self._select_all_button.clicked.connect(self._select_all_cities)
        self._deselect_all_button.clicked.connect(self._deselect_all_cities)
        self._delete_selected_cities_btn.clicked.connect(self._delete_selected_cities)
        self._manage_districts_btn.clicked.connect(self._open_district_manager)

    def _apply_styles(self) -> None:
        """Применение стилей оформления."""
        # Фон страницы
        self.setStyleSheet(f"""
            QWidget#LinkGeneratorPage {{
                background-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Заголовок страницы (20px, bold)
        self._page_title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 20px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)

        # QSplitter
        splitter = self.findChild(QSplitter, "mainSplitter")
        if splitter:
            splitter.setStyleSheet(f"""
                QSplitter#mainSplitter {{
                    background-color: transparent;
                }}
                QSplitter#mainSplitter::handle {{
                    background-color: {GLASS_BORDER};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 3px;
                }}
                QSplitter#mainSplitter::handle:hover {{
                    background-color: {ACCENT_CYAN};
                }}
            """)

        # Подсказка
        self.findChild(QLabel, "hintLabel").setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
            }}
        """)

        # Поле ввода сегмента
        self._segment_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BACKGROUND_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
                selection-background-color: {ACCENT_CYAN};
                selection-color: {BACKGROUND_PRIMARY};
            }}
            QTextEdit:focus {{
                border: 1px solid {ACCENT_CYAN};
            }}
        """)

        # Заголовки
        for obj_name in ["segmentLabel", "citiesTitle", "resultTitle"]:
            label = self.findChild(QLabel, obj_name)
            if label:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {TEXT_PRIMARY};
                        font-size: {FONT_SIZE_TITLE}px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                    }}
                """)

        # Скролл
        self._cities_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        # Чекбоксы
        for checkbox in self._city_checkboxes.values():
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {TEXT_PRIMARY};
                    font-size: {FONT_SIZE_BODY}px;
                    font-family: {FONT_FAMILY};
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 4px;
                    background-color: {BACKGROUND_TERTIARY};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ACCENT_CYAN};
                    border: 1px solid {ACCENT_CYAN};
                }}
            """)

        # Разделитель
        divider = self.findChild(QFrame, "divider")
        if divider:
            divider.setStyleSheet(
                f"background-color: {BORDER_COLOR}; min-height: 1px; max-height: 1px;"
            )

        # Кнопка генерации с glassmorphism
        self._generate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {GLASS_BUTTON_BG};
                color: {BACKGROUND_PRIMARY};
                border: 1px solid rgba(6, 182, 212, 100);
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: rgba(6, 182, 212, 220);
            }}
            QPushButton:pressed {{
                background-color: rgba(6, 182, 212, 150);
            }}
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 20);
                color: {TEXT_SECONDARY};
            }}
        """)

        # Кнопки копирования/экспорта с glassmorphism
        for button in [
            self._copy_button,
            self._export_button,
            self._select_all_button,
            self._deselect_all_button,
        ]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 10);
                    color: {TEXT_PRIMARY};
                    border: 1px solid {GLASS_BORDER};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QPushButton:hover {{
                    background-color: {GLASS_HOVER};
                    border: 1px solid rgba(255, 255, 255, 40);
                    color: {ACCENT_CYAN};
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 20);
                }}
                QPushButton:disabled {{
                    opacity: 0.5;
                }}
            """)

        # Кнопка удаления (danger)
        if hasattr(self, '_delete_selected_cities_btn'):
            self._delete_selected_cities_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(220, 38, 38, 150);
                    color: {BACKGROUND_PRIMARY};
                    border: 1px solid rgba(220, 38, 38, 100);
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QPushButton:hover {{
                    background-color: rgba(220, 38, 38, 200);
                    border: 1px solid rgba(220, 38, 38, 150);
                }}
                QPushButton:disabled {{
                    opacity: 0.5;
                }}
            """)

        # Результат с glassmorphism
        self._result_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(40, 40, 40, 80);
                color: {TEXT_PRIMARY};
                border: 1px solid {GLASS_BORDER};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: {FONT_SIZE_BODY}px;
                selection-background-color: rgba(6, 182, 212, 150);
                selection-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Статус и счётчик
        for label in [self._status_label, self._count_label]:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: {FONT_SIZE_SMALL}px;
                    font-family: {FONT_FAMILY};
                }}
            """)

    def _generate_links(self) -> None:
        """Генерация ссылок для выбранных регионов."""
        segment = self._segment_input.toPlainText().strip()

        if not segment:
            self._status_label.setText("❌ Введите поисковый запрос")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            return

        regions = self._get_selected_regions()

        if not regions:
            self._status_label.setText("❌ Выберите хотя бы один город/район")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            return

        # Генерация ссылок
        self._generated_links = generate_links_batch([segment], regions)

        # Отображение результатов
        links_text = "\n".join(
            f"{link['region']}: {link['link']}" for link in self._generated_links
        )
        self._result_input.setText(links_text)

        # Обновление статуса
        count = len(self._generated_links)
        self._count_label.setText(f"{count} ссылок")
        self._status_label.setText(f"✅ Сгенерировано {count} ссылок для '{segment}'")
        self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")

        # Активация кнопок
        self._copy_button.setEnabled(True)
        self._export_button.setEnabled(True)

        # Сигнал
        self.links_generated.emit(count)

    def _copy_links(self) -> None:
        """Копирование ссылок в буфер обмена."""
        if not self._generated_links:
            self._status_label.setText("❌ Нет ссылок для копирования")
            self._status_label.setStyleSheet(f"color: red;")
            return

        try:
            from PySide6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            links_text = "\n".join(link["link"] for link in self._generated_links)
            clipboard.setText(links_text)

            self._status_label.setText("📋 Ссылки скопированы в буфер обмена")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
        except Exception as e:
            self._status_label.setText(f"❌ Ошибка копирования: {e}")
            self._status_label.setStyleSheet(f"color: red;")

    def _export_links(self) -> None:
        """Экспорт ссылок в CSV."""
        if not self._generated_links:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить ссылки", "yandex_maps_links.csv", "CSV файлы (*.csv)"
        )

        if not filepath:
            return

        success = save_links_to_csv(self._generated_links, filepath)

        if success:
            self._status_label.setText(f"✅ Ссылки сохранены в {filepath}")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
        else:
            self._status_label.setText("❌ Ошибка сохранения")
            self._status_label.setStyleSheet(f"color: red;")
