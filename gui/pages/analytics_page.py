"""
Страница аналитики Битрикс24.

Модуль предоставляет виджет AnalyticsPage для загрузки и анализа
данных из Битрикс24 (LEAD.csv, DEAL.csv).

Classes:
    AnalyticsPage: QWidget для аналитики Битрикс24.

Example:
    >>> page = AnalyticsPage()
    >>> page.show()
"""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QDialog,
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
    TEXT_MUTED,
    GLASS_CARD_BG,
    GLASS_BORDER,
)
from modules.bitrix_analytics import analyze_bitrix, calculate_metrics
from modules.chart_generator import (
    create_funnel_chart,
    create_pie_chart,
    create_bar_chart,
)
from modules.report_exporter import create_analytics_report

CSV_OPEN_FILTER = "CSV файлы (*.csv)"
REPORT_SAVE_FILTER = "Excel файлы (*.xlsx)"
IMAGE_SAVE_FILTER = "PNG изображения (*.png)"


class AnalysisThread(QThread):
    """Поток для анализа данных Битрикс24."""

    finished = Signal(object, object, object)  # leads_df, deals_df, metrics
    error = Signal(str)

    def __init__(self, lead_filepath: str, deal_filepath: str, parent=None):
        super().__init__(parent)
        self.lead_filepath = lead_filepath
        self.deal_filepath = deal_filepath

    def run(self):
        try:
            leads, deals, metrics = analyze_bitrix(
                self.lead_filepath, self.deal_filepath
            )
            self.finished.emit(leads, deals, metrics)
        except Exception as e:
            self.error.emit(str(e))


class ChartDialog(QDialog):
    """Диалоговое окно просмотра графика."""

    def __init__(self, title: str, chart_bytes: bytes, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 800)
        self.chart_bytes = chart_bytes
        self.zoom_level = 1.0
        self.original_pixmap = QPixmap()
        self.original_pixmap.loadFromData(chart_bytes)

        self._init_ui()

    def _init_ui(self):
        """Инициализация UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Заголовок
        title_label = QLabel(self.windowTitle())
        title_label.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-size: 18px;
                font-weight: bold;
                padding: 16px;
                border-bottom: 1px solid #2A2A2A;
            }
        """)
        layout.addWidget(title_label)

        # Скролл для графика
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background-color: #121212;")

        # Лейбл для изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #121212;")
        self._apply_zoom()

        self.scroll.setWidget(self.image_label)
        layout.addWidget(self.scroll, stretch=1)

        # Панель кнопок
        button_panel = QWidget()
        button_panel.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-top: 1px solid #2A2A2A;
                padding: 12px;
            }
        """)
        button_layout = QHBoxLayout(button_panel)
        button_layout.addStretch()

        # Кнопка сохранения
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("minimalButton")
        save_btn.clicked.connect(self._save_chart)
        button_layout.addWidget(save_btn)

        # Увеличить
        zoom_in_btn = QPushButton("Увеличить +")
        zoom_in_btn.setObjectName("minimalButton")
        zoom_in_btn.clicked.connect(self._zoom_in)
        button_layout.addWidget(zoom_in_btn)

        # Уменьшить
        zoom_out_btn = QPushButton("Уменьшить -")
        zoom_out_btn.setObjectName("minimalButton")
        zoom_out_btn.clicked.connect(self._zoom_out)
        button_layout.addWidget(zoom_out_btn)

        # Сброс
        reset_btn = QPushButton("Сброс")
        reset_btn.setObjectName("minimalButton")
        reset_btn.clicked.connect(self._reset_zoom)
        button_layout.addWidget(reset_btn)

        # Закрыть
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("accentButton")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()
        layout.addWidget(button_panel)

        # Контекстное меню для сохранения
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self._show_context_menu)

    def _apply_zoom(self):
        """Применить масштабирование."""
        if self.original_pixmap.isNull():
            return

        transform = QTransform()
        transform.scale(self.zoom_level, self.zoom_level)
        scaled_pixmap = self.original_pixmap.transformed(
            transform, Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def _zoom_in(self):
        """Увеличить масштаб."""
        self.zoom_level *= 1.2
        self._apply_zoom()

    def _zoom_out(self):
        """Уменьшить масштаб."""
        self.zoom_level = max(0.1, self.zoom_level / 1.2)
        self._apply_zoom()

    def _reset_zoom(self):
        """Сбросить масштаб."""
        self.zoom_level = 1.0
        self._apply_zoom()

    def _save_chart(self):
        """Сохранить график в файл."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            f"{self.windowTitle()}.png",
            IMAGE_SAVE_FILTER,
        )

        if filepath:
            self.original_pixmap.save(filepath)

    def _show_context_menu(self, pos):
        """Показать контекстное меню."""
        menu = QMenu(self)
        save_action = menu.addAction("Сохранить график")
        action = menu.exec(self.image_label.mapToGlobal(pos))

        if action == save_action:
            self._save_chart()



class AnalyticsPage(QWidget):
    """
    Страница аналитики Битрикс24.

    Виджет предоставляет интерфейс для:
    - Загрузки LEAD.csv и DEAL.csv
    - Расчёта метрик (конверсия, воронки, категории)
    - Генерации диаграмм
    - Экспорта отчётов в Excel

    Example:
        >>> page = AnalyticsPage()
        >>> page.show()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        bitrix_analytics: "BitrixAnalytics | None" = None,
        chart_generator: "ChartGenerator | None" = None,
        report_exporter: "ReportExporter | None" = None,
    ) -> None:
        """
        Инициализация страницы аналитики.

        Args:
            parent: Родительский виджет. По умолчанию None.
            bitrix_analytics: Сервис аналитики Битрикс24.
            chart_generator: Генератор диаграмм.
            report_exporter: Экспортёр отчётов.
        """
        super().__init__(parent)
        self.setObjectName("AnalyticsPage")

        # Данные
        self._lead_filepath: str | None = None
        self._deal_filepath: str | None = None
        self._leads_df = None
        self._deals_df = None
        self._metrics: dict | None = None
        self._chart_images: dict = {}  # {chart_name: chart_bytes}
        self._chart_buttons: dict = {}  # {chart_name: QPushButton}

        # Поток анализа
        self._analysis_thread: AnalysisThread | None = None

        self._init_ui()
        self._apply_styles()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # Заголовок
        self._page_title = QLabel("Аналитика Битрикс24")
        self._page_title.setObjectName("pageTitle")
        main_layout.addWidget(self._page_title)

        # 1. Загрузка файлов
        files_group = self._create_files_group()
        main_layout.addWidget(files_group)

        # 2. Карточки метрик
        self._metrics_group = self._create_metrics_group()
        main_layout.addWidget(self._metrics_group)

        # 3. Кнопки графиков
        self._chart_status_labels: dict = {}
        self._chart_view_buttons: dict = {}
        buttons_widget = self._create_buttons_widget()
        main_layout.addWidget(buttons_widget, stretch=1)

    def _create_files_group(self) -> QWidget:
        """Создание группы загрузки файлов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Заголовок
        title_label = QLabel("Загрузка файлов Битрикс24")
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        # Подсказка
        hint_label = QLabel(
            "Загрузите файлы LEAD.csv и DEAL.csv из экспорта Битрикс24 для анализа"
        )
        hint_label.setObjectName("hintLabel")
        layout.addWidget(hint_label)

        # Кнопки загрузки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)

        self._load_lead_button = QPushButton("Загрузить LEAD.csv")
        self._load_lead_button.setObjectName("accentButton")
        buttons_layout.addWidget(self._load_lead_button)

        self._load_deal_button = QPushButton("Загрузить DEAL.csv")
        self._load_deal_button.setObjectName("accentButton")
        buttons_layout.addWidget(self._load_deal_button)

        self._analyze_button = QPushButton("Запустить анализ")
        self._analyze_button.setObjectName("processButton")
        self._analyze_button.setEnabled(False)
        buttons_layout.addWidget(self._analyze_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Статус загрузки
        self._file_status_label = QLabel("")
        self._file_status_label.setObjectName("statusLabel")
        layout.addWidget(self._file_status_label)

        return widget

    def _create_metrics_group(self) -> QWidget:
        """Создание группы карточек метрик."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Заголовок
        title_label = QLabel("Ключевые метрики")
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        # Сетка метрик (5 колонок)
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        # Создаём карточки метрик
        self._metric_cards = {}
        metric_keys = [
            ("total_leads", "Всего лидов", "{}"),
            ("total_deals", "Всего сделок", "{}"),
            ("conversion_rate", "Конверсия", "{:.1f}%"),
            ("avg_deal_value", "Средний чек", "{:,.0f} ₽"),
            ("success_rate", "Успешные", "{:.1f}%"),
        ]

        for key, title, fmt in metric_keys:
            card = self._create_metric_card(title, "-", fmt)
            self._metric_cards[key] = card
            metrics_layout.addWidget(card)

        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)

        return widget

    def _create_metric_card(self, title: str, value: str, fmt: str) -> QWidget:
        """Создание одной карточки метрики."""
        card = QWidget()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Название
        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        layout.addWidget(title_label)

        # Значение
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.fmt = fmt  # Сохраняем формат
        layout.addWidget(value_label)

        return card

    def _create_buttons_widget(self) -> QWidget:
        """Создание виджета с кнопками графиков."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Заголовок секции
        section_title = QLabel("Графики")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        # Сетка кнопок (2 колонки)
        grid = QGridLayout()
        grid.setSpacing(16)

        # Конфигурация кнопок
        chart_configs = [
            ("funnel_leads", "Воронка лидов", 0, 0),
            ("funnel_deals", "Воронка сделок", 0, 1),
            ("categories", "Категории", 1, 0),
            ("managers", "Менеджеры", 1, 1),
            ("refusals", "Причины отказа", 2, 0, 2),  # spanning 2 columns
        ]

        for config in chart_configs:
            chart_name = config[0]
            title = config[1]
            row = config[2]
            col = config[3]
            colspan = config[4] if len(config) > 4 else 1

            button = self._create_chart_button(chart_name, title)
            grid.addWidget(button, row, col, 1, colspan)
            self._chart_buttons[chart_name] = button

        grid.setColumnStretch(2, 1)  # Spacer на правой стороне
        layout.addLayout(grid)

        # Кнопка экспорта
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self._export_button = QPushButton("Экспорт отчёта в Excel")
        self._export_button.setObjectName("exportButton")
        self._export_button.setMinimumHeight(50)
        self._export_button.setMinimumWidth(280)
        self._export_button.setEnabled(False)
        self._export_button.clicked.connect(self._export_report)
        export_layout.addWidget(self._export_button)
        export_layout.addStretch()

        layout.addLayout(export_layout)
        layout.addStretch()

        return widget

    def _create_chart_button(self, chart_name: str, title: str) -> QWidget:
        """Создание кнопки графика."""
        card = QWidget()
        card.setObjectName("chartCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Название
        title_label = QLabel(title)
        title_label.setObjectName("chartTitle")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)
        layout.addWidget(title_label)

        # Статус
        status_label = QLabel("Нет данных")
        status_label.setObjectName("chartStatus")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: #A0A0A0;
                font-size: {FONT_SIZE_BODY}px;
                font-family: {FONT_FAMILY};
            }}
        """)
        layout.addWidget(status_label)
        self._chart_status_labels[chart_name] = status_label

        # Кнопка "Посмотреть"
        view_btn = QPushButton("Посмотреть")
        view_btn.setObjectName("viewChartButton")
        view_btn.setMinimumHeight(44)
        view_btn.setEnabled(False)
        view_btn.clicked.connect(lambda: self._on_view_chart_clicked(chart_name))
        layout.addWidget(view_btn)
        self._chart_view_buttons[chart_name] = view_btn

        return card

    def _create_chart_placeholder(self, title: str, width: int, height: int) -> QLabel:
        """Создание placeholder для графика."""
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumSize(width, height)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {BACKGROUND_TERTIARY};
                border: 2px solid {BORDER_COLOR};
                border-radius: 12px;
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_TITLE}px;
            }}
        """)
        return label

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._load_lead_button.clicked.connect(self._load_lead_file)
        self._load_deal_button.clicked.connect(self._load_deal_file)
        self._analyze_button.clicked.connect(self._start_analysis)

    def _apply_styles(self) -> None:
        """Применение стилей."""
        # Фон страницы
        self.setStyleSheet(f"""
            QWidget#AnalyticsPage {{
                background-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Заголовок страницы
        self._page_title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)

        # Заголовки секций
        for obj_name in ["sectionTitle", "chartSectionTitle"]:
            for label in self.findChildren(QLabel, obj_name):
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {ACCENT_CYAN};
                        font-size: 18px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        padding: 8px 0;
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

        # Кнопки
        self._load_lead_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_CYAN};
                color: {BACKGROUND_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: #0891B2;
            }}
        """)
        self._load_deal_button.setStyleSheet(self._load_lead_button.styleSheet())

        self._analyze_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {STATUS_SUCCESS};
                color: {BACKGROUND_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:disabled {{
                background-color: {BORDER_COLOR};
                color: {TEXT_SECONDARY};
            }}
        """)

        # Карточки метрик с glassmorphism
        for card in self._metric_cards.values():
            card.setStyleSheet(f"""
                QWidget#metricCard {{
                    background-color: {GLASS_CARD_BG};
                    border: 1px solid {GLASS_BORDER};
                    border-radius: 10px;
                }}
            """)
            title_label = card.findChild(QLabel, "metricTitle")
            if title_label:
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: #FFFFFF;
                        background-color: transparent;
                        font-size: {FONT_SIZE_SMALL}px;
                        font-family: {FONT_FAMILY};
                        font-weight: bold;
                    }}
                """)
            value_label = card.findChild(QLabel, "metricValue")
            if value_label:
                value_label.setStyleSheet(f"""
                    QLabel {{
                        color: #FFFFFF;
                        background-color: transparent;
                        font-size: 24px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                    }}
                """)

        # Карточки графиков с glassmorphism
        for card in self._chart_buttons.values():
            card.setStyleSheet(f"""
                QWidget#chartCard {{
                    background-color: {GLASS_CARD_BG};
                    border: 1px solid {GLASS_BORDER};
                    border-radius: 10px;
                }}
            """)
            title_label = card.findChild(QLabel, "chartTitle")
            if title_label:
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: #FFFFFF;
                        background-color: transparent;
                        font-size: 16px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                    }}
                """)
            status_label = card.findChild(QLabel, "chartStatus")
            if status_label:
                status_label.setStyleSheet(f"""
                    QLabel {{
                        color: #A0A0A0;
                        background-color: transparent;
                        font-size: {FONT_SIZE_SMALL}px;
                        font-family: {FONT_FAMILY};
                    }}
                """)
            view_btn = card.findChild(QPushButton, "viewChartButton")
            if view_btn:
                view_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(6, 182, 212, 150);
                        color: {TEXT_PRIMARY};
                        border: 1px solid rgba(6, 182, 212, 80);
                        border-radius: 6px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(6, 182, 212, 200);
                    }}
                    QPushButton:disabled {{
                        background-color: rgba(255, 255, 255, 20);
                        color: {TEXT_MUTED};
                    }}
                """)

        # Кнопки диалога графиков
        for btn_name in ["minimalButton", "accentButton"]:
            for btn in self.findChildren(QPushButton, btn_name):
                if btn_name == "minimalButton":
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: rgba(255, 255, 255, 10);
                            color: {TEXT_PRIMARY};
                            border: 1px solid {GLASS_BORDER};
                            border-radius: 8px;
                            padding: 10px 20px;
                            font-family: {FONT_FAMILY};
                            font-size: {FONT_SIZE_BODY}px;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(255, 255, 255, 20);
                            border: 1px solid rgba(255, 255, 255, 40);
                            color: {ACCENT_CYAN};
                        }}
                    """)
                elif btn_name == "accentButton":
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: rgba(6, 182, 212, 150);
                            color: {TEXT_PRIMARY};
                            border: 1px solid rgba(6, 182, 212, 80);
                            border-radius: 8px;
                            padding: 10px 20px;
                            font-weight: bold;
                            font-family: {FONT_FAMILY};
                            font-size: {FONT_SIZE_BODY}px;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(6, 182, 212, 200);
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

        # Кнопка экспорта
        if hasattr(self, "_export_button") and self._export_button:
            self._export_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {STATUS_SUCCESS};
                    color: {BACKGROUND_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    padding: 14px 28px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QPushButton:hover {{
                    background-color: #059669;
                }}
                QPushButton:disabled {{
                    background-color: {BORDER_COLOR};
                    color: {TEXT_SECONDARY};
                }}
            """)

    def _select_csv_file(self, title: str) -> str | None:
        """Открывает диалог выбора CSV-файла и возвращает путь."""
        filepath, _ = QFileDialog.getOpenFileName(self, title, "", CSV_OPEN_FILTER)
        return filepath or None

    def _load_lead_file(self) -> None:
        """Загрузка файла LEAD.csv."""
        filepath = self._select_csv_file("Загрузить LEAD.csv")

        if filepath:
            self._lead_filepath = filepath
            self._update_file_status()

    def _load_deal_file(self) -> None:
        """Загрузка файла DEAL.csv."""
        filepath = self._select_csv_file("Загрузить DEAL.csv")

        if filepath:
            self._deal_filepath = filepath
            self._update_file_status()

    def _update_file_status(self) -> None:
        """Обновление статуса загрузки файлов."""
        status_parts = []
        if self._lead_filepath:
            status_parts.append(f"✅ LEAD: {Path(self._lead_filepath).name}")
        if self._deal_filepath:
            status_parts.append(f"✅ DEAL: {Path(self._deal_filepath).name}")

        if status_parts:
            self._file_status_label.setText(" | ".join(status_parts))
            self._file_status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            self._analyze_button.setEnabled(
                self._lead_filepath is not None and self._deal_filepath is not None
            )
        else:
            self._file_status_label.setText("")

    def _start_analysis(self) -> None:
        """Запуск анализа данных."""
        if not self._lead_filepath or not self._deal_filepath:
            return

        self._analyze_button.setEnabled(False)
        self._file_status_label.setText("⏳ Анализ данных...")

        self._analysis_thread = AnalysisThread(
            self._lead_filepath, self._deal_filepath, parent=self
        )
        self._analysis_thread.finished.connect(self._on_analysis_finished)
        self._analysis_thread.error.connect(self._on_analysis_error)
        self._analysis_thread.start()

    def _on_analysis_finished(self, leads_df, deals_df, metrics) -> None:
        """Обработчик завершения анализа."""
        self._leads_df = leads_df
        self._deals_df = deals_df
        self._metrics = metrics

        # Обновление метрик
        self._update_metrics(metrics)

        # Генерация графиков
        self._generate_charts(leads_df, deals_df, metrics)

        self._file_status_label.setText("✅ Анализ завершён")
        self._export_button.setEnabled(True)

    def _on_view_chart_clicked(self, chart_name: str) -> None:
        """Открыть диалог просмотра графика."""
        chart_bytes = self._chart_images.get(chart_name)
        if not chart_bytes:
            return

        titles = {
            "funnel_leads": "Воронка лидов",
            "funnel_deals": "Воронка сделок",
            "categories": "Категории лидов",
            "managers": "Эффективность менеджеров",
            "refusals": "Причины отказа",
        }

        dialog = ChartDialog(titles.get(chart_name, "График"), chart_bytes, self)
        dialog.exec()

    def _on_analysis_error(self, error_message: str) -> None:
        """Обработчик ошибки анализа."""
        self._file_status_label.setText(f"❌ {error_message}")
        self._file_status_label.setStyleSheet("color: red;")
        self._analyze_button.setEnabled(True)

    def _update_metrics(self, metrics: dict) -> None:
        """Обновление карточек метрик."""
        metric_mapping = {
            "total_leads": ("Всего лидов", "{}"),
            "total_deals": ("Всего сделок", "{}"),
            "conversion_rate": ("Конверсия", "{:.1f}%"),
            "avg_deal_value": ("Средний чек", "{:,.0f} ₽"),
            "success_rate": ("Успешные", "{:.1f}%"),
        }

        for key, (title, fmt) in metric_mapping.items():
            if key in self._metric_cards and key in metrics:
                value = metrics[key]
                value_label = self._metric_cards[key].findChild(QLabel, "metricValue")
                if value_label:
                    value_label.setText(fmt.format(value))

    def _generate_charts(self, leads_df, deals_df, metrics) -> None:
        """Генерация графиков."""
        try:
            # 1. Воронка лидов
            if "funnel_leads" in self._chart_buttons:
                funnel_data = metrics.get("lead_stages", {})
                if funnel_data:
                    stages = list(funnel_data.keys())
                    values = [int(v) for v in funnel_data.values()]
                    chart_bytes = create_funnel_chart(
                        stages, values, "Воронка лидов", dark_theme=True
                    )
                    self._chart_images["funnel_leads"] = chart_bytes
                    self._update_chart_button(
                        "funnel_leads", f"{len(stages)} стадий", True
                    )

            # 2. Воронка сделок
            if "funnel_deals" in self._chart_buttons:
                funnel_data = metrics.get("deal_stages", {})
                if funnel_data:
                    stages = list(funnel_data.keys())
                    values = [int(v) for v in funnel_data.values()]
                    chart_bytes = create_funnel_chart(
                        stages, values, "Воронка сделок", dark_theme=True
                    )
                    self._chart_images["funnel_deals"] = chart_bytes
                    self._update_chart_button(
                        "funnel_deals", f"{len(stages)} стадий", True
                    )

            # 3. Категории
            if "categories" in self._chart_buttons:
                categories_data = metrics.get("leads_by_category", {})
                if categories_data:
                    chart_bytes = create_pie_chart(
                        categories_data, "Категории лидов", dark_theme=True
                    )
                    self._chart_images["categories"] = chart_bytes
                    self._update_chart_button(
                        "categories", f"{len(categories_data)} категорий", True
                    )

            # 4. Менеджеры
            if "managers" in self._chart_buttons:
                managers_data = metrics.get("leads_by_manager", {})
                if managers_data:
                    chart_bytes = create_bar_chart(
                        managers_data, "Эффективность менеджеров", dark_theme=True
                    )
                    self._chart_images["managers"] = chart_bytes
                    self._update_chart_button(
                        "managers", f"{len(managers_data)} менеджеров", True
                    )

            # 5. Причины отказа
            if "refusals" in self._chart_buttons:
                refusals_data = metrics.get("lead_refusals", {})
                if refusals_data:
                    chart_bytes = create_pie_chart(
                        refusals_data, "Причины отказа", dark_theme=True
                    )
                    self._chart_images["refusals"] = chart_bytes
                    self._update_chart_button(
                        "refusals", f"{len(refusals_data)} причин", True
                    )

        except Exception as e:
            print(f"Ошибка генерации графиков: {e}")
            import traceback

            traceback.print_exc()

    def _update_chart_button(
        self, chart_name: str, status_text: str, enabled: bool
    ) -> None:
        """Обновить кнопку графика."""
        if chart_name in self._chart_status_labels:
            self._chart_status_labels[chart_name].setText(status_text)
        if chart_name in self._chart_view_buttons:
            self._chart_view_buttons[chart_name].setEnabled(enabled)

    def _display_chart(self, chart_name: str, chart_bytes: bytes) -> None:
        """Отображение графика."""
        if chart_name not in self._chart_labels:
            return

        label = self._chart_labels[chart_name]
        pixmap = QPixmap()
        pixmap.loadFromData(chart_bytes)
        label.setPixmap(pixmap)
        label.setText("")  # Убираем текст

        # Сохраняем данные для возможного диалога
        self._chart_images[chart_name] = chart_bytes

    def _export_report(self) -> None:
        """Экспорт отчёта в Excel."""
        if not self._metrics or self._leads_df is None or self._deals_df is None:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            f"bitrix_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            REPORT_SAVE_FILTER,
        )

        if filepath:
            try:
                create_analytics_report(
                    self._metrics, self._leads_df, self._deals_df, filepath
                )
                self._file_status_label.setText(f"✅ Отчёт сохранён: {filepath}")
                self._file_status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            except Exception as e:
                self._file_status_label.setText(f"❌ Ошибка экспорта: {e}")
                self._file_status_label.setStyleSheet("color: red;")
