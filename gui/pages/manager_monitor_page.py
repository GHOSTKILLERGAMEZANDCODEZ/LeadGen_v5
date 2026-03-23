"""
Страница мониторинга менеджеров Битрикс24.

Модуль предоставляет виджет ManagerMonitorPage для отслеживания
распределения лидов по менеджерам через вебхук Битрикс24.

Classes:
    ManagerMonitorPage: QWidget для мониторинга менеджеров.
    WebhookLoadThread: Поток для загрузки данных из Битрикс24.
    ExclusionDialog: Диалог для исключения менеджеров.

Example:
    >>> page = ManagerMonitorPage()
    >>> page.show()
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
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
    QWidget,
    QComboBox,
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
    STATUS_WARNING,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
)
from modules.bitrix_webhook import get_leads_distribution
from utils.config_loader import load_config, save_config


class WebhookLoadThread(QThread):
    """Поток для загрузки данных из Битрикс24."""

    finished = Signal(dict, dict, bool)  # managers, distribution, success
    error = Signal(str)

    def __init__(self, webhook_url: str, status_name: str, parent=None):
        super().__init__(parent)
        self.webhook_url = webhook_url
        self.status_name = status_name

    def run(self):
        try:
            managers, distribution, success = get_leads_distribution(
                self.webhook_url, self.status_name, max_leads=10000
            )
            self.finished.emit(managers, distribution, success)
        except Exception as e:
            self.error.emit(str(e))


class ExclusionDialog(QDialog):
    """Диалог для исключения менеджеров."""

    def __init__(self, managers: dict, excluded: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Исключить менеджеров")
        self.setMinimumSize(500, 600)
        self.managers = managers
        self.excluded = excluded.copy()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Описание
        desc = QLabel(
            "Выберите менеджеров для исключения из мониторинга:\n"
            "✓ Отметьте галочкой для исключения"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;")
        layout.addWidget(desc)

        # Список менеджеров
        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list_widget)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        apply_btn = QPushButton("Применить")
        apply_btn.setObjectName("accentButton")
        apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(apply_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._populate_list()

    def _populate_list(self):
        """Заполнить список менеджеров."""
        self.list_widget.clear()
        all_managers = set(self.managers.keys()) | set(self.excluded)

        for manager in sorted(all_managers):
            item = QListWidgetItem(manager)
            item.setCheckState(
                Qt.CheckState.Checked
                if manager in self.excluded
                else Qt.CheckState.Unchecked
            )
            self.list_widget.addItem(item)

    def _on_item_changed(self, item: QListWidgetItem):
        """Обработка изменения чекбокса."""
        manager = item.text()
        if item.checkState() == Qt.CheckState.Checked:
            if manager not in self.excluded:
                self.excluded.append(manager)
        else:
            if manager in self.excluded:
                self.excluded.remove(manager)

    def get_excluded(self) -> list:
        """Получить список исключённых."""
        return self.excluded


class ManagerCard(QFrame):
    """Карточка менеджера с glassmorphism."""

    def __init__(self, name: str, leads_count: int, parent=None):
        super().__init__(parent)
        self.name = name
        self.leads_count = leads_count

        # Применяем glassmorphism стиль к виджету
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {GLASS_CARD_BG};
                border: 1px solid {GLASS_BORDER};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border: 1px solid rgba(255, 255, 255, 50);
                background-color: rgba(50, 50, 50, 120);
            }}
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Имя
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 16px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.name_label)

        # Количество лидов
        self.leads_label = QLabel(f"{self.leads_count} лидов")
        self.leads_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_BODY}px;
                font-family: {FONT_FAMILY};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.leads_label)

        # Статус
        status, color = self._get_status(self.leads_count)
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: {FONT_SIZE_BODY}px;
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.status_label)

    def _get_status(self, count: int) -> tuple:
        """Определить статус по количеству лидов."""
        if count < 30:
            return "В норме", STATUS_SUCCESS
        elif count < 50:
            return "Перегружен", STATUS_WARNING
        else:
            return "Критично", STATUS_ERROR


class ManagerMonitorPage(QWidget):
    """
    Страница мониторинга менеджеров Битрикс24.

    Example:
        >>> page = ManagerMonitorPage()
        >>> page.show()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        bitrix_client: "BitrixWebhookClient | None" = None,
    ) -> None:
        """
        Инициализация страницы мониторинга менеджеров.

        Args:
            parent: Родительский виджет. По умолчанию None.
            bitrix_client: Клиент Битрикс24 API.
        """
        super().__init__(parent)
        self.setObjectName("ManagerMonitorPage")

        # Загрузка конфигурации
        self._config = load_config()
        self._webhook_url = self._config.get("bitrix_webhook", {}).get(
            "webhook_url", ""
        )
        self._status_name = self._config.get("bitrix_webhook", {}).get(
            "status_id", "Новая заявка"
        )
        self._excluded_managers = self._config.get("bitrix_webhook", {}).get(
            "excluded_managers", []
        )

        # Данные
        self._managers: dict[str, str] = {}
        self._distribution: dict[str, int] = {}
        self._filtered_managers: dict[str, int] = {}

        # Поток загрузки
        self._load_thread: WebhookLoadThread | None = None

        self._init_ui()
        self._apply_styles()
        self._connect_signals()

    def _init_ui(self):
        """Инициализация UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Заголовок
        self._page_title = QLabel("Мониторинг менеджеров")
        self._page_title.setObjectName("pageTitle")
        layout.addWidget(self._page_title)

        # Панель настроек
        settings_panel = self._create_settings_panel()
        layout.addWidget(settings_panel)

        # Панель поиска и фильтрации
        filter_panel = self._create_filter_panel()
        layout.addWidget(filter_panel)

        # Скролл для карточек (прозрачный)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(f"background-color: transparent;")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll, stretch=1)

        # Статус
        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

    def _create_settings_panel(self) -> QWidget:
        """Панель настроек вебхука."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # URL вебхука
        layout.addWidget(QLabel("URL вебхука:"))
        self._webhook_input = QLineEdit(self._webhook_url)
        self._webhook_input.setPlaceholderText(
            "https://your-company.bitrix24.ru/rest/1/xxxxx/"
        )
        self._webhook_input.setMinimumWidth(400)
        layout.addWidget(self._webhook_input)

        # Статус
        layout.addWidget(QLabel("Статус:"))
        self._status_combo = QComboBox()
        self._status_combo.addItems(["Новая заявка", "В работе", "Выставлен счёт"])
        self._status_combo.setCurrentText(self._status_name)
        layout.addWidget(self._status_combo)

        # Кнопка загрузки
        self._load_button = QPushButton("Загрузить данные")
        self._load_button.setObjectName("accentButton")
        layout.addWidget(self._load_button)

        return widget

    def _create_filter_panel(self) -> QWidget:
        """Панель поиска и сортировки."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Поиск
        layout.addWidget(QLabel("🔍 Поиск:"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Поиск по имени...")
        self._search_input.setMinimumWidth(250)
        layout.addWidget(self._search_input)

        # Сортировка
        layout.addWidget(QLabel("Сортировка:"))
        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["По количеству лидов", "По имени (А-Я)"])
        layout.addWidget(self._sort_combo)

        # Кнопка исключений
        self._exclusion_button = QPushButton("Исключить менеджеров")
        self._exclusion_button.setObjectName("minimalButton")
        self._exclusion_button.setEnabled(False)
        layout.addWidget(self._exclusion_button)

        layout.addStretch()
        return widget

    def _connect_signals(self):
        """Подключение сигналов."""
        self._load_button.clicked.connect(self._start_loading)
        self._search_input.textChanged.connect(self._filter_managers)
        self._sort_combo.currentTextChanged.connect(self._filter_managers)
        self._exclusion_button.clicked.connect(self._open_exclusion_dialog)

    def _apply_styles(self):
        """Применение стилей с glassmorphism."""
        self.setStyleSheet(f"""
            QWidget#ManagerMonitorPage {{
                background-color: transparent;
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

        # Панель настроек
        for label in self.findChildren(QLabel):
            if label.text() in ["URL вебхука:", "Статус:", "🔍 Поиск:", "Сортировка:"]:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {TEXT_SECONDARY};
                        font-size: {FONT_SIZE_BODY}px;
                        font-family: {FONT_FAMILY};
                    }}
                """)

        # Поля ввода с glassmorphism
        for input_widget in self.findChildren(QLineEdit):
            input_widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: rgba(30, 30, 30, 60);
                    color: {TEXT_PRIMARY};
                    border: 1px solid {GLASS_BORDER};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {ACCENT_CYAN};
                }}
            """)

        # Кнопки с glassmorphism
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == "accentButton":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(6, 182, 212, 100);
                        color: {BACKGROUND_PRIMARY};
                        border: 1px solid rgba(6, 182, 212, 60);
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(6, 182, 212, 150);
                    }}
                """)
            elif btn.objectName() == "minimalButton":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(255, 255, 255, 5);
                        color: {TEXT_PRIMARY};
                        border: 1px solid {GLASS_BORDER};
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(255, 255, 255, 10);
                        border: 1px solid rgba(255, 255, 255, 40);
                        color: {ACCENT_CYAN};
                    }}
                """)

        # Статус
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _start_loading(self):
        """Начать загрузку данных."""
        self._webhook_url = self._webhook_input.text().strip()
        self._status_name = self._status_combo.currentText()

        if not self._webhook_url:
            self._status_label.setText("❌ Введите URL вебхука")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        self._load_button.setEnabled(False)
        self._status_label.setText("⏳ Загрузка данных из Битрикс24...")

        self._load_thread = WebhookLoadThread(
            self._webhook_url, self._status_name, self
        )
        self._load_thread.finished.connect(self._on_loading_finished)
        self._load_thread.error.connect(self._on_loading_error)
        self._load_thread.start()

    def _on_loading_finished(self, managers: dict, distribution: dict, success: bool):
        """Обработка завершения загрузки."""
        self._load_button.setEnabled(True)

        if not success:
            self._status_label.setText("❌ Ошибка загрузки данных")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        self._managers = managers
        self._distribution = distribution
        self._exclusion_button.setEnabled(True)

        # Сохранение настроек
        self._config["bitrix_webhook"]["webhook_url"] = self._webhook_url
        self._config["bitrix_webhook"]["status_id"] = self._status_name
        save_config(self._config)

        self._filter_managers()
        self._status_label.setText(f"✅ Загружено {len(managers)} менеджеров")
        self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")

    def _on_loading_error(self, error: str):
        """Обработка ошибки загрузки."""
        self._load_button.setEnabled(True)
        self._status_label.setText(f"❌ {error}")
        self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _filter_managers(self):
        """Фильтрация и сортировка менеджеров."""
        search_text = self._search_input.text().lower()
        sort_by = self._sort_combo.currentText()

        # Фильтрация по исключениям и поиску
        filtered = {}
        for name, count in self._distribution.items():
            if name in self._excluded_managers:
                continue
            if search_text and search_text not in name.lower():
                continue
            filtered[name] = count

        # Сортировка
        if sort_by == "По имени (А-Я)":
            filtered = dict(sorted(filtered.items()))
        else:  # По количеству лидов
            filtered = dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True))

        self._filtered_managers = filtered
        self._render_cards()

    def _render_cards(self):
        """Отрисовка карточек менеджеров."""
        # Очистка
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Создание карточек
        row, col = 0, 0
        max_cols = 4

        for name, count in self._filtered_managers.items():
            card = ManagerCard(name, count)
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Добавляем растягиватель в последнюю строку
        if col > 0:
            for c in range(col, max_cols):
                spacer = QWidget()
                self.cards_layout.addWidget(spacer, row, c)

    def _open_exclusion_dialog(self):
        """Открыть диалог исключений."""
        # Проверяем что данные загружены
        if not self._managers:
            self._status_label.setText("❌ Сначала загрузите данные")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
            return
        
        dialog = ExclusionDialog(self._managers, self._excluded_managers, self)
        if dialog.exec() == QDialog.Accepted:
            self._excluded_managers = dialog.get_excluded()
            
            # Гарантируем существование раздела bitrix_webhook
            if "bitrix_webhook" not in self._config:
                self._config["bitrix_webhook"] = {}
            
            self._config["bitrix_webhook"][
                "excluded_managers"
            ] = self._excluded_managers
            
            if save_config(self._config):
                # Обновляем карточки
                self._filter_managers()
                self._status_label.setText("✅ Менеджеры исключены")
                self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            else:
                self._status_label.setText("❌ Ошибка сохранения")
                self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
