"""
Анимированный sidebar с Material Icons для навигации по приложению.

Модуль предоставляет компоненты для создания боковой панели навигации
с анимацией расширения/свёртывания при наведении курсора.

Classes:
    SidebarButton: Кнопка навигации с иконкой Material Icons (наследуется от QPushButton).
    Sidebar: Основная панель навигации с анимацией.

Example:
    >>> sidebar = Sidebar()
    >>> sidebar.page_changed.connect(self.on_page_changed)
    >>> layout.addWidget(sidebar)
"""

from typing import Final

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
    Signal,
    QEvent,
)
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from gui.styles.theme import (
    ACCENT_CYAN,
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_TITLE,
    SIDEBAR_ANIMATION_DURATION,
    SIDEBAR_COLLAPSED_WIDTH,
    SIDEBAR_EXPANDED_WIDTH,
    TEXT_SECONDARY,
    GLASS_SIDEBAR_BG,
    GLASS_BORDER,
    GLASS_HOVER,
)

# =============================================================================
# Константы навигации
# =============================================================================

NAVIGATION_ITEMS: Final[list[dict[str, str]]] = [
    {"id": "home", "icon": "\ue88a", "text": "Главная"},  # home
    {"id": "processing", "icon": "\ue2c7", "text": "Обработка лидов"},  # folder_open
    {"id": "analytics", "icon": "\ue641", "text": "Аналитика Битрикс"},  # bar_chart
    {"id": "links", "icon": "\ue157", "text": "Генератор ссылок"},  # link
    {"id": "lpr", "icon": "\ue888", "text": "Поиск ЛПР"},  # person_search
    {"id": "managers", "icon": "\ue7fe", "text": "Мониторинг"},  # supervisor_account
]

SETTINGS_ITEM: Final[dict[str, str]] = {
    "id": "settings",
    "icon": "\ue8b8",  # settings
    "text": "Настройки",
}

# Стили для sidebar (glassmorphism)
SIDEBAR_STYLESHEET: Final[str] = f"""
QWidget#SidebarWidget {{
    background-color: {GLASS_SIDEBAR_BG};
    border-right: 1px solid {GLASS_BORDER};
}}

QLabel#LogoLabel {{
    color: {ACCENT_CYAN};
    font-size: 16px;
    font-weight: bold;
    font-family: {FONT_FAMILY};
}}

QLabel#DividerLine {{
    background-color: {GLASS_BORDER};
    min-height: 1px;
    max-height: 1px;
}}

QLabel#IconLabel {{
    color: {TEXT_SECONDARY};
    font-size: 24px;
    font-family: 'Material Icons';
    background-color: transparent;
}}

QLabel#TextLabel {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_BODY}px;
    font-family: {FONT_FAMILY};
    background-color: transparent;
}}
"""

# Стили для кнопок (QPushButton) с glassmorphism
BUTTON_STYLESHEET: Final[str] = f"""
QPushButton#SidebarButton {{
    background-color: transparent;
    border: none;
    border-radius: 0px;
    padding-left: 8px;
    text-align: left;
}}

QPushButton#SidebarButton:hover {{
    background-color: {GLASS_HOVER};
}}

QPushButton#SidebarButton:pressed {{
    background-color: transparent;
}}
"""

# Стили для активной кнопки (QPushButton) с glassmorphism
ACTIVE_BUTTON_STYLESHEET: Final[str] = f"""
QPushButton#SidebarButton {{
    background-color: transparent;
    border: none;
    border-radius: 0px;
    padding-left: 8px;
    text-align: left;
}}

QPushButton#SidebarButton:hover {{
    background-color: transparent;
}}

QPushButton#SidebarButton:pressed {{
    background-color: transparent;
}}
"""

# Стили для текста активной кнопки с glassmorphism
ACTIVE_TEXT_STYLE: Final[str] = f"""
QLabel#TextLabel {{
    color: {ACCENT_CYAN};
    font-size: {FONT_SIZE_BODY}px;
    font-family: {FONT_FAMILY};
    font-weight: 500;
}}
"""

# Стили для иконки активной кнопки с glassmorphism
ACTIVE_ICON_STYLE: Final[str] = f"""
QLabel#IconLabel {{
    color: {ACCENT_CYAN};
    font-size: 24px;
    font-family: 'Material Icons';
}}
"""


class SidebarButton(QPushButton):
    """
    Кнопка навигации sidebar с иконкой Material Icons.
    
    Наследуется от QPushButton для встроенной поддержки кликов и hover состояний.
    """

    def __init__(self, icon: str, text: str, parent: QWidget | None = None) -> None:
        """
        Инициализация кнопки sidebar.

        Args:
            icon: Название иконки Material Icons (например, "dashboard").
            text: Текст кнопки для отображения в развёрнутом состоянии.
            parent: Родительский виджет.
        """
        super().__init__(parent)

        self._is_active: bool = False
        self._icon: str = icon
        self._text: str = text
        self._page_id: str = ""

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса кнопки."""
        self.setFixedSize(52, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("SidebarButton")
        self.setStyleSheet(BUTTON_STYLESHEET)

        # Создание layout для кнопки
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(12)

        # Иконка - Material Icons с правильным шрифтом
        self.icon_label = QLabel(self._icon)
        self.icon_label.setObjectName("IconLabel")
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Устанавливаем шрифт Material Icons через QFont
        icon_font = QFont("Material Icons", 28)
        icon_font.setStyleHint(QFont.StyleHint.Fantasy)
        self.icon_label.setFont(icon_font)
        
        # Разрешаем клики проходить через QLabel к QPushButton
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Текст
        self.text_label = QLabel(self._text)
        self.text_label.setObjectName("TextLabel")
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self.text_label.setHidden(True)  # Скрыт по умолчанию
        
        # Разрешаем клики проходить через QLabel к QPushButton
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Добавление элементов в layout
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        # Spacer для правильного позиционирования
        spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        layout.addSpacerItem(spacer)

    def _connect_signals(self) -> None:
        """Подключение сигналов кнопки."""
        # Используем встроенный сигнал clicked от QPushButton
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self) -> None:
        """Обработчик клика по кнопке."""
        # Испускаем сигнал через parent Sidebar
        # Кнопка находится в buttons_container -> content_widget -> Sidebar
        # Проверяем несколько уровней вложенности
        parent_widget = self.parent()
        grandparent = parent_widget.parent() if parent_widget else None
        greatgrandparent = grandparent.parent() if grandparent else None
        
        if isinstance(grandparent, Sidebar):
            grandparent._on_button_clicked(self._page_id)
        elif isinstance(greatgrandparent, Sidebar):
            greatgrandparent._on_button_clicked(self._page_id)

    def set_page_id(self, page_id: str) -> None:
        """
        Установка идентификатора страницы.

        Args:
            page_id: Идентификатор страницы для навигации.
        """
        self._page_id = page_id

    def set_active(self, active: bool) -> None:
        """
        Установка активного состояния кнопки.

        Args:
            active: True для активной кнопки, False для неактивной.
        """
        self._is_active = active

        if active:
            self.setStyleSheet(ACTIVE_BUTTON_STYLESHEET)
            self.text_label.setStyleSheet(ACTIVE_TEXT_STYLE)
            self.icon_label.setStyleSheet(ACTIVE_ICON_STYLE)
        else:
            self.setStyleSheet(BUTTON_STYLESHEET)
            self.text_label.setStyleSheet("")
            self.icon_label.setStyleSheet("")

    def set_expanded(self, expanded: bool) -> None:
        """
        Установка режима отображения текста.

        Args:
            expanded: True для отображения текста, False для скрытия.
        """
        self.text_label.setHidden(not expanded)

        if expanded:
            # В развёрнутом режиме кнопка имеет фиксированную ширину
            self.setFixedWidth(244)  # 260 - 16 (padding sidebar)
        else:
            # В свёрнутом режиме только иконка
            self.setFixedWidth(52)

    def enterEvent(self, event: QEvent) -> None:
        """
        Обработчик события входа курсора.

        Args:
            event: Событие входа курсора.
        """
        super().enterEvent(event)
        # Hover эффект обрабатывается через stylesheet

    def leaveEvent(self, event: QEvent) -> None:
        """
        Обработчик события выхода курсора.

        Args:
            event: Событие выхода курсора.
        """
        super().leaveEvent(event)
        # Hover эффект обрабатывается через stylesheet


class Sidebar(QWidget):
    """
    Основная панель навигации с анимацией расширения/свёртывания.

    Sidebar отображает логотип приложения, кнопки навигации и кнопку
    настроек. Автоматически расширяется при наведении курсора и
    сворачивается при уходе курсора.

    Attributes:
        page_changed: Сигнал с идентификатором выбранной страницы.

    Signals:
        page_changed(str): Испускается при изменении активной страницы.

    Example:
        >>> sidebar = Sidebar()
        >>> sidebar.page_changed.connect(self.handle_page_change)
        >>> main_layout.addWidget(sidebar)
    """

    page_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Инициализация sidebar.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        self.setObjectName("SidebarWidget")
        self._is_expanded: bool = False
        self._active_page: str = "home"

        # Анимация
        self._animation_group: QParallelAnimationGroup | None = None
        self._width_animation_min: QPropertyAnimation | None = None
        self._width_animation_max: QPropertyAnimation | None = None

        self._setup_ui()
        self._setup_animation()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса sidebar."""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Контейнер для содержимого
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 16, 8, 16)
        content_layout.setSpacing(16)

        # Логотип
        logo_label = QLabel("LeadGen")
        logo_label.setObjectName("LogoLabel")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_font = QFont(FONT_FAMILY, FONT_SIZE_TITLE, QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        content_layout.addWidget(logo_label)

        # Разделитель после логотипа
        divider_top = QLabel()
        divider_top.setObjectName("DividerLine")
        divider_top.setFixedHeight(1)
        content_layout.addWidget(divider_top)

        # Контейнер для кнопок навигации
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)

        # Создание кнопок навигации
        self._buttons: dict[str, SidebarButton] = {}

        for item in NAVIGATION_ITEMS:
            button = SidebarButton(item["icon"], item["text"])
            button.set_page_id(item["id"])
            self._buttons[item["id"]] = button
            buttons_layout.addWidget(button)

        content_layout.addWidget(buttons_container)

        # Spacer для прижатия настроек к низу
        spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        content_layout.addSpacerItem(spacer)

        # Разделитель перед настройками
        divider_settings = QLabel()
        divider_settings.setObjectName("DividerLine")
        divider_settings.setFixedHeight(1)
        content_layout.addWidget(divider_settings)

        # Кнопка настроек
        settings_button = SidebarButton(SETTINGS_ITEM["icon"], SETTINGS_ITEM["text"])
        settings_button.set_page_id(SETTINGS_ITEM["id"])
        self._buttons[SETTINGS_ITEM["id"]] = settings_button
        content_layout.addWidget(settings_button)

        layout.addWidget(content_widget)

        # Установка начальной ширины
        self.setFixedWidth(SIDEBAR_COLLAPSED_WIDTH)

    def _setup_animation(self) -> None:
        """Настройка анимации расширения/свёртывания."""
        # Анимация для minimumWidth
        self._width_animation_min = QPropertyAnimation(self, b"minimumWidth")
        self._width_animation_min.setDuration(SIDEBAR_ANIMATION_DURATION)
        self._width_animation_min.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Анимация для maximumWidth
        self._width_animation_max = QPropertyAnimation(self, b"maximumWidth")
        self._width_animation_max.setDuration(SIDEBAR_ANIMATION_DURATION)
        self._width_animation_max.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Группа параллельных анимаций
        self._animation_group = QParallelAnimationGroup()
        self._animation_group.addAnimation(self._width_animation_min)
        self._animation_group.addAnimation(self._width_animation_max)

    def _apply_styles(self) -> None:
        """Применение стилей к sidebar."""
        self.setStyleSheet(SIDEBAR_STYLESHEET)

    def _expand(self) -> None:
        """Расширение sidebar до полной ширины."""
        if self._is_expanded or self._animation_group is None:
            return

        self._is_expanded = True

        if self._width_animation_min and self._width_animation_max:
            self._width_animation_min.setEndValue(SIDEBAR_EXPANDED_WIDTH)
            self._width_animation_max.setEndValue(SIDEBAR_EXPANDED_WIDTH)

            # Обновление состояния кнопок
            for button in self._buttons.values():
                button.set_expanded(True)

            self._animation_group.start()

    def _collapse(self) -> None:
        """Свёртывание sidebar до минимальной ширины."""
        if not self._is_expanded or self._animation_group is None:
            return

        self._is_expanded = False

        if self._width_animation_min and self._width_animation_max:
            self._width_animation_min.setEndValue(SIDEBAR_COLLAPSED_WIDTH)
            self._width_animation_max.setEndValue(SIDEBAR_COLLAPSED_WIDTH)

            # Обновление состояния кнопок
            for button in self._buttons.values():
                button.set_expanded(False)

            self._animation_group.start()

    def set_active_page(self, page_id: str) -> None:
        """
        Установка активной страницы.

        Метод обновляет визуальное состояние кнопок и испускает
        сигнал page_changed с идентификатором страницы.

        Args:
            page_id: Идентификатор активной страницы.

        Example:
            >>> sidebar.set_active_page("analytics")
        """
        if page_id == self._active_page:
            return

        self._active_page = page_id

        # Обновление состояния кнопок
        for button_id, button in self._buttons.items():
            button.set_active(button_id == page_id)

    def _on_button_clicked(self, page_id: str) -> None:
        """
        Обработчик клика по кнопке навигации.

        Метод устанавливает активную страницу и испускает сигнал page_changed.

        Args:
            page_id: Идентификатор страницы для активации.

        Example:
            >>> sidebar._on_button_clicked("analytics")
        """
        self.set_active_page(page_id)
        self.page_changed.emit(page_id)

    def get_active_page(self) -> str:
        """
        Получение идентификатора активной страницы.

        Returns:
            str: Идентификатор текущей активной страницы.
        """
        return self._active_page

    def enterEvent(self, event: QEvent) -> None:
        """
        Обработчик события входа курсора в область sidebar.

        Запускает анимацию расширения sidebar.

        Args:
            event: Событие входа курсора.
        """
        super().enterEvent(event)
        self._expand()

    def leaveEvent(self, event: QEvent) -> None:
        """
        Обработчик события выхода курсора из области sidebar.

        Запускает анимацию свёртывания sidebar.

        Args:
            event: Событие выхода курсора.
        """
        super().leaveEvent(event)
        self._collapse()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Обработчик события нажатия кнопки мыши.

        Args:
            event: Событие нажатия кнопки мыши.
        """
        # Игнорирование кликов вне кнопок для предотвращения сворачивания
        super().mousePressEvent(event)
