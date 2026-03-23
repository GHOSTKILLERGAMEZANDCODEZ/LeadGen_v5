"""
Страница поиска ЛПР (Лиц Принимающих Решения).

Модуль предоставляет виджет LPRFinderPage для парсинга сайтов компаний
и поиска информации о ЛПР: ФИО, должности, ИНН, телефоны, email.

Classes:
    LPRFinderPage: QWidget для поиска ЛПР.
    LPRSearchThread: Поток для поиска ЛПР на сайтах.

Example:
    >>> page = LPRFinderPage()
    >>> page.show()
"""

from datetime import datetime
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
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
    STATUS_ERROR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
)
from modules.lpr_parser import search_lpr_on_website, save_lpr_to_csv

CSV_OPEN_FILTER = "CSV файлы (*.csv)"
CSV_SAVE_FILTER = "CSV файлы (*.csv)"


class LPRSearchThread(QThread):
    """Поток для поиска ЛПР на сайтах компаний."""

    progress = Signal(int, str)  # прогресс, статус
    finished = Signal(list)  # результаты
    error = Signal(str)

    def __init__(self, companies: list[dict], parent=None):
        super().__init__(parent)
        self.companies = companies

    def run(self):
        try:
            results = []
            total = len(self.companies)

            for i, company in enumerate(self.companies, 1):
                self.progress.emit(
                    int(i / total * 100),
                    f"Обработка {i} из {total}: {company.get('name', 'Без названия')}",
                )

                # Получаем URL сайта
                url = company.get("url", "")

                if url and url.strip():
                    # Реальный парсинг сайта
                    result = search_lpr_on_website(url)
                    result["company_name"] = company.get("name", "")
                    result["url"] = url
                else:
                    # Нет сайта
                    result = {
                        "company_name": company.get("name", ""),
                        "url": "",
                        "fio": "",
                        "position": "",
                        "inn": "",
                        "phones": "",
                        "emails": "",
                    }

                results.append(result)

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class LPRFinderPage(QWidget):
    """
    Страница поиска ЛПР (Лиц Принимающих Решения).

    Example:
        >>> page = LPRFinderPage()
        >>> page.show()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        lpr_parser: "LPRParser | None" = None,
    ) -> None:
        """
        Инициализация страницы поиска ЛПР.

        Args:
            parent: Родительский виджет. По умолчанию None.
            lpr_parser: Парсер ЛПР.
        """
        super().__init__(parent)
        self.setObjectName("LPRFinderPage")

        # Данные
        self._companies: list[dict] = []
        self._lpr_results: list[dict] = []
        self._search_thread: LPRSearchThread | None = None

        self._init_ui()
        self._apply_styles()
        self._connect_signals()

    def _init_ui(self):
        """Инициализация UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Заголовок
        self._page_title = QLabel("Поиск ЛПР")
        self._page_title.setObjectName("pageTitle")
        layout.addWidget(self._page_title)

        # 1. Загрузка файла
        file_group = self._create_file_group()
        layout.addWidget(file_group)

        # 2. Прогресс
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                text-align: center;
                height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_CYAN};
                border-radius: 5px;
            }}
        """)
        layout.addWidget(self._progress_bar)

        self._progress_label = QLabel("")
        self._progress_label.setVisible(False)
        self._progress_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;"
        )
        layout.addWidget(self._progress_label)

        # 3. Таблица результатов
        result_group = self._create_result_group()
        layout.addWidget(result_group, stretch=1)

    def _create_file_group(self) -> QFrame:
        """Группа загрузки файла."""
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("Загрузка файла с компаниями")
        title.setObjectName("settingsCardTitle")
        layout.addWidget(title)

        # Описание
        desc = QLabel(
            "Загрузите CSV файл со списком компаний для поиска ЛПР.\nФормат: название компании, URL сайта"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_BODY}px;")
        layout.addWidget(desc)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)

        self._load_btn = QPushButton("Загрузить CSV")
        self._load_btn.setObjectName("accentButton")
        buttons_layout.addWidget(self._load_btn)

        self._search_btn = QPushButton("Запустить поиск ЛПР")
        self._search_btn.setObjectName("accentButton")
        self._search_btn.setEnabled(False)
        buttons_layout.addWidget(self._search_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Статус
        self._file_status_label = QLabel("")
        self._file_status_label.setObjectName("settingsStatus")
        layout.addWidget(self._file_status_label)

        return card

    def _create_result_group(self) -> QFrame:
        """Группа результатов."""
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("Результаты поиска")
        title.setObjectName("settingsCardTitle")
        layout.addWidget(title)

        # Таблица
        self._results_table = QTableWidget()
        self._results_table.setColumnCount(7)
        self._results_table.setHorizontalHeaderLabels(
            ["Компания", "ФИО", "Должность", "ИНН", "Телефон", "Email", "Сайт"]
        )
        self._results_table.horizontalHeader().setStretchLastSection(True)
        self._results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self._results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BACKGROUND_TERTIARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                gridline-color: {BORDER_COLOR};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {BACKGROUND_SECONDARY};
                color: {TEXT_PRIMARY};
                padding: 10px;
                border: none;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)
        layout.addWidget(self._results_table)

        # Кнопка экспорта
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self._export_btn = QPushButton("Экспорт в CSV")
        self._export_btn.setObjectName("minimalButton")
        self._export_btn.setEnabled(False)
        export_layout.addWidget(self._export_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        return card

    def _connect_signals(self):
        """Подключение сигналов."""
        self._load_btn.clicked.connect(self._load_csv)
        self._search_btn.clicked.connect(self._start_search)
        self._export_btn.clicked.connect(self._export_results)

    def _apply_styles(self):
        """Применение стилей."""
        self.setStyleSheet(f"""
            QWidget#LPRFinderPage {{
                background-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Заголовок
        self._page_title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)

        # Карточки с glassmorphism (более прозрачные)
        for card in self.findChildren(QFrame, "settingsCard"):
            card.setStyleSheet(f"""
                QFrame#settingsCard {{
                    background-color: rgba(30, 30, 30, 60);
                    border: 1px solid rgba(255, 255, 255, 30);
                    border-radius: 10px;
                }}
            """)

        # Заголовки карточек
        for label in self.findChildren(QLabel, "settingsCardTitle"):
            label.setStyleSheet(f"""
                QLabel {{
                    color: {ACCENT_CYAN};
                    font-size: 18px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Кнопки
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == "accentButton":
                btn.setStyleSheet(f"""
                    QPushButton#accentButton {{
                        background-color: {ACCENT_CYAN};
                        color: {BACKGROUND_PRIMARY};
                        border: none;
                        border-radius: 6px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#accentButton:hover {{
                        background-color: {ACCENT_CYAN_HOVER};
                    }}
                """)
            elif btn.objectName() == "minimalButton":
                btn.setStyleSheet(f"""
                    QPushButton#minimalButton {{
                        background-color: transparent;
                        color: {TEXT_SECONDARY};
                        border: 1px solid {BORDER_COLOR};
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#minimalButton:hover {{
                        border: 1px solid {ACCENT_CYAN};
                        color: {ACCENT_CYAN};
                    }}
                """)

        # Статус
        self._file_status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _load_csv(self):
        """Загрузка CSV файла."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Загрузить CSV с компаниями", "", CSV_OPEN_FILTER
        )

        if not filepath:
            return

        try:
            # Чтение CSV
            import csv

            self._companies = []
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._companies.append(
                        {
                            "name": row.get("Название", row.get("name", "")),
                            "url": row.get(
                                "companyUrl", row.get("url", row.get("website", ""))
                            ),
                        }
                    )

            self._file_status_label.setText(
                f"✅ Загружено {len(self._companies)} компаний"
            )
            self._file_status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            self._search_btn.setEnabled(len(self._companies) > 0)

        except Exception as e:
            self._file_status_label.setText(f"❌ Ошибка загрузки: {e}")
            self._file_status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _start_search(self):
        """Запуск поиска ЛПР."""
        if not self._companies:
            return

        self._search_btn.setEnabled(False)
        self._load_btn.setEnabled(False)
        self._progress_bar.setVisible(True)
        self._progress_label.setVisible(True)

        self._search_thread = LPRSearchThread(self._companies, self)
        self._search_thread.progress.connect(self._on_search_progress)
        self._search_thread.finished.connect(self._on_search_finished)
        self._search_thread.error.connect(self._on_search_error)
        self._search_thread.start()

    def _on_search_progress(self, progress: int, status: str):
        """Обновление прогресса."""
        self._progress_bar.setValue(progress)
        self._progress_label.setText(status)

    def _on_search_finished(self, results: list[dict]):
        """Завершение поиска."""
        self._lpr_results = results
        self._search_btn.setEnabled(True)
        self._load_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._progress_label.setVisible(False)

        # Отображение результатов
        self._display_results(results)

        self._file_status_label.setText(
            f"✅ Найдено ЛПР: {len([r for r in results if r.get('fio')])} из {len(results)}"
        )
        self._file_status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
        self._export_btn.setEnabled(len(results) > 0)

    def _on_search_error(self, error: str):
        """Ошибка поиска."""
        self._search_btn.setEnabled(True)
        self._load_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._progress_label.setVisible(False)

        self._file_status_label.setText(f"❌ {error}")
        self._file_status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _display_results(self, results: list[dict]):
        """Отображение результатов в таблице."""
        self._results_table.setRowCount(len(results))

        for i, result in enumerate(results):
            self._results_table.setItem(
                i, 0, QTableWidgetItem(result.get("company_name", ""))
            )
            self._results_table.setItem(i, 1, QTableWidgetItem(result.get("fio", "")))
            self._results_table.setItem(
                i, 2, QTableWidgetItem(result.get("position", ""))
            )
            self._results_table.setItem(i, 3, QTableWidgetItem(result.get("inn", "")))
            self._results_table.setItem(
                i, 4, QTableWidgetItem(result.get("phones", ""))
            )
            self._results_table.setItem(
                i, 5, QTableWidgetItem(result.get("emails", ""))
            )
            self._results_table.setItem(i, 6, QTableWidgetItem(result.get("url", "")))

    def _export_results(self):
        """Экспорт результатов в CSV."""
        if not self._lpr_results:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты",
            f"lpr_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            CSV_SAVE_FILTER,
        )

        if filepath:
            try:
                save_lpr_to_csv(self._lpr_results, filepath)
                self._file_status_label.setText(f"✅ Результаты сохранены: {filepath}")
                self._file_status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            except Exception as e:
                self._file_status_label.setText(f"❌ Ошибка экспорта: {e}")
                self._file_status_label.setStyleSheet(f"color: {STATUS_ERROR};")
