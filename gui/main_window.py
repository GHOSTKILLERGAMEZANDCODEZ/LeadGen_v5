"""
Главное окно приложения LeadGen v5.

Модуль предоставляет основной контейнер приложения с sidebar навигацией
и интеграцией всех страниц через QStackedWidget.

Classes:
    MainWindow: QMainWindow с sidebar навигацией и переключением страниц.

Example:
    >>> from gui.main_window import MainWindow
    >>> window = MainWindow()
    >>> window.show()
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from gui.pages.home_page import HomePage
from gui.pages.processing_page import ProcessingPage
from gui.pages.analytics_page import AnalyticsPage
from gui.pages.link_generator_page import LinkGeneratorPage
from gui.pages.lpr_finder_page import LPRFinderPage
from gui.pages.manager_monitor_page import ManagerMonitorPage
from gui.pages.settings_page import SettingsPage
from gui.sidebar import Sidebar
from gui.styles.stylesheet import get_main_stylesheet
from gui.styles.theme import FONT_FAMILY, FONT_SIZE_BODY
from utils.windows_blur import (
    apply_glass_effect,
    apply_acrylic_effect,
    remove_glass_effect,
    remove_acrylic_effect,
    set_blur_intensity,
)


class MainWindow(QMainWindow):
    """
    Главное окно приложения с sidebar навигацией.

    Окно содержит анимированный sidebar слева и QStackedWidget для
    переключения между страницами приложения. Поддерживает навигацию
    через sidebar и программные переходы.

    Attributes:
        toast_manager: Менеджер toast уведомлений.

    Example:
        >>> from core.dependency_container import DependencyContainer
        >>> container = DependencyContainer()
        >>> window = MainWindow(container=container)
        >>> window.show()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        container: "DependencyContainer | None" = None,
    ) -> None:
        """
        Инициализация главного окна.

        Args:
            parent: Родительский виджет. По умолчанию None.
            container: Контейнер зависимостей. Если None, создаётся новый.
        """
        super().__init__(parent)

        # DependencyContainer
        from core.dependency_container import DependencyContainer
        self._container = container or DependencyContainer()
        self._config = self._container.config

        # Загрузка настройки прозрачности из конфигурации
        self._transparency_enabled: bool = self._config.get("ui", {}).get("transparency_enabled", True)
        self._blur_intensity: int = self._config.get("ui", {}).get("blur_intensity", 100)

        self._setup_window_properties()
        self._init_ui()
        self._setup_connections()
        self._apply_styles()

    def _setup_window_properties(self) -> None:
        """
        Настройка свойств окна.

        Устанавливает заголовок, размеры, шрифт и другие свойства
        главного окна приложения.
        """
        self.setWindowTitle("LeadGen v5")
        self.setWindowIcon(QIcon("images/icon.ico"))
        self.setMinimumSize(1280, 720)
        self.resize(1400, 900)

        # Настройка шрифта
        font = QFont(FONT_FAMILY, FONT_SIZE_BODY)
        self.setFont(font)

        # High DPI scaling включается автоматически в PySide6
        # WA_EnableHighDpiScaling устарел и удалён в PySide6 6.5+

    def _init_ui(self) -> None:
        """
        Инициализация пользовательского интерфейса.

        Создаёт central widget, QHBoxLayout для sidebar + content,
        sidebar и QStackedWidget со всеми страницами.
        """
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        # Основной layout (sidebar + content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (анимированный, слева)
        self._sidebar = Sidebar()
        main_layout.addWidget(self._sidebar)

        # QStackedWidget для переключения страниц
        self._stack = QStackedWidget()
        self._stack.setObjectName("PageStack")
        main_layout.addWidget(self._stack)

        # Создание и добавление страниц (по порядку)
        self._pages: dict[str, QWidget] = {}

        # 0. HomePage
        self._home_page = HomePage()
        self._pages["home"] = self._home_page
        self._stack.addWidget(self._home_page)

        # 1. ProcessingPage — с Dependency Injection сервиса
        processing_service = self._container.get_processing_service()
        self._processing_page = ProcessingPage(
            processing_service=processing_service,
        )
        self._pages["processing"] = self._processing_page
        self._stack.addWidget(self._processing_page)

        # 2. AnalyticsPage
        self._analytics_page = AnalyticsPage()
        self._pages["analytics"] = self._analytics_page
        self._stack.addWidget(self._analytics_page)

        # 3. LinkGeneratorPage
        self._link_generator_page = LinkGeneratorPage()
        self._pages["links"] = self._link_generator_page
        self._stack.addWidget(self._link_generator_page)

        # 4. LPRFinderPage
        self._lpr_finder_page = LPRFinderPage()
        self._pages["lpr"] = self._lpr_finder_page
        self._stack.addWidget(self._lpr_finder_page)

        # 5. ManagerMonitorPage
        self._manager_monitor_page = ManagerMonitorPage()
        self._pages["managers"] = self._manager_monitor_page
        self._stack.addWidget(self._manager_monitor_page)

        # 6. SettingsPage
        self._settings_page = SettingsPage()
        self._pages["settings"] = self._settings_page
        self._stack.addWidget(self._settings_page)

    def _setup_connections(self) -> None:
        """
        Подключение сигналов между компонентами.

        Соединяет:
        - sidebar.page_changed → _on_page_changed(page_id)
        - home_page.navigate_to → _navigate_to(page_id)
        - processing_page.process_started → _on_process_started(files, managers)
        """
        # Sidebar navigation
        self._sidebar.page_changed.connect(self._on_page_changed)

        # Home page navigation
        self._home_page.navigate_to.connect(self._navigate_to)

        # Processing page signals
        self._processing_page.process_started.connect(self._on_process_started)

        # Settings page - прозрачность интерфейса
        self._settings_page.transparency_changed.connect(self.set_transparency_enabled)

        # Settings page - интенсивность размытия
        self._settings_page.blur_intensity_changed.connect(self.set_blur_intensity)

        # Settings page - обновление городов в генераторе ссылок
        self._settings_page.settings_saved.connect(self._link_generator_page.reload_cities)

    def _apply_styles(self) -> None:
        """
        Применение стилей оформления.

        Устанавливает полную таблицу стилей приложения и фон
        для content области.
        """
        # Применение полной таблицы стилей
        self.setStyleSheet(get_main_stylesheet())

        central_widget = self.centralWidget()

        # Фон content области (прозрачный или сплошной)
        if self._transparency_enabled:
            self._stack.setStyleSheet("""
                QStackedWidget#PageStack {
                    background-color: transparent;
                }
            """)

            if central_widget:
                central_widget.setStyleSheet("""
                    QWidget#CentralWidget {
                        background-color: transparent;
                    }
                """)

            # Применяем Windows DWM blur эффект с указанной интенсивностью
            apply_acrylic_effect(self, self._blur_intensity)
            if central_widget:
                apply_glass_effect(central_widget)
        else:
            # Сначала отключаем эффекты прозрачности
            remove_acrylic_effect(self)
            if central_widget:
                remove_glass_effect(central_widget)

            # Затем устанавливаем сплошной фон
            self._stack.setStyleSheet("""
                QStackedWidget#PageStack {
                    background-color: #1a1a2e;
                }
            """)

            if central_widget:
                central_widget.setStyleSheet("""
                    QWidget#CentralWidget {
                        background-color: #1a1a2e;
                    }
                """)

    def set_transparency_enabled(self, enabled: bool) -> None:
        """
        Включение/отключение прозрачности фона.

        Args:
            enabled: True для включения прозрачности, False для отключения.

        Example:
            >>> self.set_transparency_enabled(False)
        """
        if self._transparency_enabled == enabled:
            return

        self._transparency_enabled = enabled
        self._apply_styles()

    def set_blur_intensity(self, intensity: int) -> None:
        """
        Установка интенсивности размытия фона.

        Args:
            intensity: Интенсивность от 0 до 100.

        Example:
            >>> self.set_blur_intensity(50)
        """
        # Ограничиваем диапазон
        intensity = max(0, min(100, intensity))

        if self._blur_intensity == intensity:
            return

        self._blur_intensity = intensity

        # Применяем эффект только если прозрачность включена
        if self._transparency_enabled:
            central_widget = self.centralWidget()
            set_blur_intensity(self, intensity)
            if central_widget:
                apply_glass_effect(central_widget)

    def _on_page_changed(self, page_id: str) -> None:
        """
        Обработчик изменения активной страницы.

        Переключает QStackedWidget на страницу с указанным идентификатором
        и обновляет состояние sidebar.

        Args:
            page_id: Идентификатор страницы для отображения.

        Example:
            >>> self._on_page_changed("analytics")
        """
        if page_id not in self._pages:
            return

        widget = self._pages[page_id]
        index = self._stack.indexOf(widget)

        if index >= 0:
            self._stack.setCurrentIndex(index)
            self._sidebar.set_active_page(page_id)

    def _navigate_to(self, page_id: str) -> None:
        """
        Программная навигация к странице.

        Метод позволяет переключиться на указанную страницу
        программно, например, из быстрых переходов на HomePage.

        Args:
            page_id: Идентификатор целевой страницы.

        Example:
            >>> self._navigate_to("processing")
        """
        self._on_page_changed(page_id)

    def _on_process_started(self, files: list[str], managers: list[str]) -> None:
        """
        Обработчик начала обработки файлов.

        Отображает toast уведомление о начале обработки с указанием
        количества файлов.

        Args:
            files: Список путей к файлам для обработки.
            managers: Список имён менеджеров для обработки.

        Example:
            >>> self._on_process_started(["file1.xlsx"], ["Manager 1"])
        """
        # Toast notifications removed - status shown in ProcessingPage
        pass
