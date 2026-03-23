"""
Главная страница приложения LeadGen v5.

Модуль содержит виджет HomePage с приветствием и быстрыми переходами
к основным разделам приложения.

Example:
    >>> from gui.pages import HomePage
    >>> home = HomePage()
    >>> home.navigate_to.connect(lambda page_id: print(f"Navigate to: {page_id}"))
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Signal, Qt

from ..styles.theme import (
    BACKGROUND_PRIMARY,
    BACKGROUND_SECONDARY,
    ACCENT_CYAN,
    ACCENT_CYAN_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    BORDER_COLOR,
    FONT_FAMILY,
    FONT_SIZE_TITLE,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
)


class HomePage(QWidget):
    """
    Главная страница с приветствием и быстрыми переходами.

    Виджет отображает заголовок приложения, краткое описание
    и кнопки для быстрого перехода к основным разделам системы.

    Attributes:
        navigate_to: Сигнал с ID страницы для перехода.

    Signals:
        navigate_to (str): Испускается при нажатии на кнопку перехода.
    """

    navigate_to = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Инициализирует главную страницу.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._init_ui()
        self._apply_styles()

    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс.

        Создаёт структуру виджета с приветствием, разделителем
        и кнопками быстрых переходов.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        # Секция приветствия
        greeting_section = self._create_greeting_section()
        layout.addWidget(greeting_section)

        # Разделитель
        separator = self._create_separator()
        layout.addWidget(separator)

        # Секция быстрых переходов
        quick_links_section = self._create_quick_links_section()
        layout.addWidget(quick_links_section)

        # Добавляем растягиватель для центрирования контента
        layout.addStretch()

    def _create_greeting_section(self) -> QWidget:
        """
        Создаёт секцию приветствия.

        Returns:
            QWidget с заголовком, описанием и логотипом.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Логотип (по центру, растянут)
        logo_label = QLabel()
        logo_label.setObjectName("logoImage")
        logo_pixmap = QPixmap("images/Text.png")
        if not logo_pixmap.isNull():
            # Масштабируем с сохранением пропорций
            scaled_pixmap = logo_pixmap.scaled(
                400, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        # Центрируем логотип
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Заголовок
        title_label = QLabel("Добро пожаловать в LeadGen")
        title_label.setObjectName("greetingTitle")
        title_font = QFont(FONT_FAMILY, 24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Описание
        description_label = QLabel(
            "Автоматизированная система обработки лидов и аналитики.\n"
            "Управляйте продажами эффективно с помощью современных инструментов."
        )
        description_label.setObjectName("greetingDescription")
        description_font = QFont(FONT_FAMILY, FONT_SIZE_BODY)
        description_label.setFont(description_font)
        layout.addWidget(description_label)

        return widget

    def _create_separator(self) -> QFrame:
        """
        Создаёт горизонтальный разделитель.

        Returns:
            QFrame в виде горизонтальной линии.
        """
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        return separator

    def _create_quick_links_section(self) -> QWidget:
        """
        Создаёт секцию быстрых переходов.

        Returns:
            QWidget с заголовком и кнопками переходов.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Заголовок секции
        title_label = QLabel("Быстрые переходы")
        title_label.setObjectName("quickLinksTitle")
        title_font = QFont(FONT_FAMILY, FONT_SIZE_TITLE)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Кнопки переходов (горизонтально)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        # Кнопка "Обработка лидов"
        leads_button = self._create_navigation_button(
            text="Обработка лидов",
            page_id="processing",
            is_accent=True,
        )
        buttons_layout.addWidget(leads_button)

        # Кнопка "Аналитика"
        analytics_button = self._create_navigation_button(
            text="Аналитика",
            page_id="analytics",
            is_accent=False,
        )
        buttons_layout.addWidget(analytics_button)

        # Кнопка "Настройки"
        settings_button = self._create_navigation_button(
            text="Настройки",
            page_id="settings",
            is_accent=False,
        )
        buttons_layout.addWidget(settings_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return widget

    def _create_navigation_button(
        self,
        text: str,
        page_id: str,
        is_accent: bool = False,
    ) -> QPushButton:
        """
        Создаёт кнопку навигации.

        Args:
            text: Текст кнопки.
            page_id: ID страницы для перехода.
            is_accent: Флаг акцентной кнопки.

        Returns:
            QPushButton с настроенным стилем и сигналом.
        """
        button = QPushButton(text)
        button.setObjectName("accentButton" if is_accent else "minimalButton")
        button.setFont(QFont(FONT_FAMILY, FONT_SIZE_BODY))
        button.setMinimumHeight(44)
        button.setMinimumWidth(180)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Подключаем сигнал навигации
        button.clicked.connect(lambda: self.navigate_to.emit(page_id))

        return button

    def _apply_styles(self) -> None:
        """
        Применяет стили оформления к виджету.

        Устанавливает фон страницы и стилизует все дочерние элементы
        согласно дизайн-системе приложения.
        """
        # Фон страницы с glassmorphism (прозрачный)
        self.setStyleSheet(f"""
            QWidget#HomePage {{
                background-color: transparent;
            }}
        """)

        # Логотип
        logo_label = self.findChild(QLabel, "logoImage")
        if logo_label:
            logo_label.setStyleSheet(f"""
                QLabel#logoImage {{
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                }}
            """)

        # Заголовок приветствия
        greeting_title = self.findChild(QLabel, "greetingTitle")
        if greeting_title:
            greeting_title.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    font-size: 24px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Описание
        greeting_desc = self.findChild(QLabel, "greetingDescription")
        if greeting_desc:
            greeting_desc.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: {FONT_SIZE_BODY}px;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Разделитель
        separator = self.findChild(QFrame, "separator")
        if separator:
            separator.setStyleSheet(f"""
                QFrame {{
                    background-color: {BORDER_COLOR};
                    max-height: 1px;
                    min-height: 1px;
                }}
            """)

        # Заголовок быстрых переходов
        quick_links_title = self.findChild(QLabel, "quickLinksTitle")
        if quick_links_title:
            quick_links_title.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    font-size: {FONT_SIZE_TITLE}px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Стили кнопок с glassmorphism
        for button in self.findChildren(QPushButton):
            if button.objectName() == "accentButton":
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {GLASS_BUTTON_BG};
                        color: {BACKGROUND_PRIMARY};
                        border: 1px solid rgba(6, 182, 212, 100);
                        border-radius: 8px;
                        padding: 12px 24px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(6, 182, 212, 220);
                    }}
                    QPushButton:pressed {{
                        background-color: rgba(6, 182, 212, 150);
                    }}
                """)
            elif button.objectName() == "minimalButton":
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(255, 255, 255, 10);
                        color: {TEXT_PRIMARY};
                        border: 1px solid {GLASS_BORDER};
                        border-radius: 8px;
                        padding: 12px 24px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(255, 255, 255, 20);
                        border-color: rgba(255, 255, 255, 40);
                    }}
                    QPushButton:pressed {{
                        background-color: rgba(255, 255, 255, 15);
                    }}
                """)
