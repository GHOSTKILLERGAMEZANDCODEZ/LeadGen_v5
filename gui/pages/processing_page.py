"""
Страница обработки лидов.

Модуль предоставляет виджет ProcessingPage для обработки лидов с
интерфейсом загрузки файлов и управления менеджерами.

Classes:
    ProcessingPage: QWidget для обработки лидов с файлами и менеджерами.
"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components.file_list import FileListWidget
from gui.components.file_loader import FileLoaderWidget
from gui.utils import ThreadCleanupMixin
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
    STATUS_ERROR,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
    GLASS_HOVER,
)
from gui.threads import ProcessingThread, ExportThread
from utils.config_loader import load_config, get_processing_settings
from database.db_manager import DatabaseManager
from modules.services.processing_service import ProcessingService

CSV_SAVE_FILTER = "CSV файлы (*.csv)"


class ProcessingPage(ThreadCleanupMixin, QWidget):
    """
    Страница обработки лидов.

    Виджет предоставляет интерфейс для загрузки файлов через Drag&Drop,
    управления списком файлов, ввода менеджеров и запуска обработки.

    Attributes:
        process_started: Сигнал, испускаемый при начале обработки.
            Передаёт списки файлов и менеджеров.

    Example:
        >>> page = ProcessingPage()
        >>> page.process_started.connect(lambda files, managers: print(f"Processing {len(files)} files with {len(managers)} managers"))
        >>> page.show()
    """

    # Сигнал с файлами и менеджерами для обработки
    process_started = Signal(list, list)

    def __init__(
        self,
        processing_service: ProcessingService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Инициализация страницы обработки лидов.

        Args:
            processing_service: Сервис для обработки (DI для тестирования).
                По умолчанию None (создаётся сервис по умолчанию).
            parent: Родительский виджет. По умолчанию None.
        """
        super().__init__(parent)
        self.setObjectName("ProcessingPage")

        # Загрузка конфигурации
        self._config = load_config()
        self._processing_settings = get_processing_settings()

        # ✅ Dependency Injection через конструктор
        self._service = processing_service or self._create_default_service()

        # Данные для экспорта
        self._df: object | None = None  # DataFrame с обработанными данными
        self._stats: dict | None = None

        # Потоки
        self._processing_thread: ProcessingThread | None = None
        self._export_thread: ExportThread | None = None

        self._init_ui()
        self._apply_styles()
        self._connect_signals()

    def _create_default_service(self) -> ProcessingService:
        """
        Создаёт сервис по умолчанию (для production).

        Returns:
            ProcessingService: Сервис обработки с реальными зависимостями
        """
        db_path = self._config.get("paths", {}).get("database", "data/database.db")
        db_manager = DatabaseManager(db_path)
        return ProcessingService(db_manager, self._config)

    def _init_ui(self) -> None:
        """
        Инициализация пользовательского интерфейса.

        Новая структура (без верхнего отступа):
        - Заголовок "Обработка лидов"
        - Горизонтальная компоновка: слева загрузка файлов, справа менеджеры
        - Список загруженных файлов внизу
        """
        # Основной layout - убираем верхний отступ
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убрали все отступы
        main_layout.setSpacing(0)  # Убрали межэлементные отступы

        # Контейнер для контента с внутренними отступами
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)  # Внутренние отступы
        content_layout.setSpacing(32)  # Отступы между элементами

        # Заголовок страницы
        self._page_title = QLabel("Обработка лидов")
        self._page_title.setObjectName("pageTitle")
        content_layout.addWidget(self._page_title)

        # Горизонтальная компоновка: загрузка файлов + менеджеры
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(32)

        # Левая часть: Загрузка файлов (50% ширины)
        left_widget = self._create_file_loader_panel()
        horizontal_layout.addWidget(left_widget, stretch=1)

        # Правая часть: Менеджеры (50% ширины)
        right_widget = self._create_managers_panel()
        horizontal_layout.addWidget(right_widget, stretch=1)

        content_layout.addLayout(horizontal_layout)

        # Список загруженных файлов
        files_widget = self._create_files_list_panel()
        content_layout.addWidget(files_widget)

        main_layout.addWidget(content_widget)

    def _create_file_loader_panel(self) -> QWidget:
        """
        Создание панели загрузки файлов.

        Returns:
            QWidget с FileLoaderWidget.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # FileLoaderWidget (Drag&Drop зона)
        self._file_loader = FileLoaderWidget()
        layout.addWidget(self._file_loader)

        return widget

    def _create_managers_panel(self) -> QWidget:
        """
        Создание панели менеджеров.

        Returns:
            QWidget с заголовком, QTextEdit, кнопкой и status label.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Заголовок "Менеджеры" (16px, bold)
        managers_title = QLabel("Менеджеры")
        managers_title.setObjectName("managersTitle")
        layout.addWidget(managers_title)

        # QTextEdit для ввода менеджеров
        self._managers_input = QTextEdit()
        self._managers_input.setObjectName("managersInput")
        self._managers_input.setPlaceholderText("Менеджер 1\nМенеджер 2...")
        self._managers_input.setMaximumHeight(150)
        layout.addWidget(self._managers_input)

        # Кнопка "🚀 Очистить и объединить"
        self._process_button = QPushButton("🚀 Очистить и объединить")
        self._process_button.setObjectName("accentButton")
        self._process_button.setMinimumHeight(48)
        self._process_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self._process_button)

        # Кнопка "Экспортировать в Битрикс" (скрыта по умолчанию)
        self._export_button = QPushButton("Экспортировать в Битрикс")
        self._export_button.setObjectName("exportButton")
        self._export_button.setMinimumHeight(48)
        self._export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._export_button.setVisible(False)  # Скрыта пока нет обработанных данных
        layout.addWidget(self._export_button)

        # Status label (для сообщений об ошибках/успехе)
        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        return widget

    def _create_files_list_panel(self) -> QWidget:
        """
        Создание панели списка файлов.

        Returns:
            QWidget с FileListWidget.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # FileListWidget (список файлов с кнопками)
        self._file_list = FileListWidget()
        layout.addWidget(self._file_list)

        return widget

    def _connect_signals(self) -> None:
        """
        Подключение сигналов между компонентами.

        Соединяет сигнал FileLoaderWidget с FileListWidget для
        добавления выбранных файлов в список.
        """
        self._file_loader.files_selected.connect(self._file_list.add_files)
        self._process_button.clicked.connect(self._on_process_clicked)
        self._export_button.clicked.connect(self._on_export_clicked)

    def _apply_styles(self) -> None:
        """
        Применение стилей оформления к виджету.

        Устанавливает фон страницы и стилизует все дочерние элементы
        согласно дизайн-системе приложения.
        """
        # Фон страницы
        self.setStyleSheet(f"""
            QWidget#ProcessingPage {{
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

        # Заголовок "Менеджеры" (16px, bold)
        managers_title = self.findChild(QLabel, "managersTitle")
        if managers_title:
            managers_title.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    font-size: {FONT_SIZE_TITLE}px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # QTextEdit для менеджеров (прозрачный)
        self._managers_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(30, 30, 30, 60);
                color: {TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 8px;
                padding: 12px;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
                selection-background-color: rgba(6, 182, 212, 100);
                selection-color: {BACKGROUND_PRIMARY};
            }}
            QTextEdit:focus {{
                border: 1px solid {ACCENT_CYAN};
            }}
            QTextEdit:disabled {{
                background-color: rgba(40, 40, 40, 40);
                color: {TEXT_SECONDARY};
            }}
        """)

        # Кнопка обработки (accentButton) с glassmorphism
        self._process_button.setStyleSheet(f"""
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

        # Кнопка экспорта (exportButton) с glassmorphism
        self._export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(16, 185, 129, 150);
                color: {BACKGROUND_PRIMARY};
                border: 1px solid rgba(16, 185, 129, 100);
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: rgba(16, 185, 129, 200);
            }}
            QPushButton:pressed {{
                background-color: rgba(16, 185, 129, 130);
            }}
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 20);
                color: {TEXT_SECONDARY};
            }}
        """)

        # Status label
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _get_managers(self) -> list[str]:
        """
        Получение списка менеджеров из поля ввода.

        Извлекает текст из QTextEdit, разбивает по строкам,
        удаляет пустые строки и пробелы.

        Returns:
            Список имён менеджеров (непустые строки).
        """
        text = self._managers_input.toPlainText()
        managers = [line.strip() for line in text.split("\n") if line.strip()]
        return managers

    def _get_files(self) -> list[str]:
        """
        Получение списка файлов из виджета списка.

        Returns:
            Список путей к файлам.
        """
        return self._file_list.get_file_paths()

    def _set_status(self, message: str, is_error: bool = False) -> None:
        """
        Установка сообщения статуса.

        Args:
            message: Текст сообщения.
            is_error: Если True, использует красный цвет (ошибка),
                иначе зелёный (успех).
        """
        self._status_label.setText(message)
        color = STATUS_ERROR if is_error else STATUS_SUCCESS
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _clear_status(self) -> None:
        """
        Очистка сообщения статуса.

        Сбрасывает текст и возвращает стандартный серый цвет.
        """
        self._status_label.setText("")
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _on_process_clicked(self) -> None:
        """
        Обработка нажатия кнопки запуска обработки.

        Запускает обработку файлов в фоновом потоке:
        - Проверка наличия файлов и менеджеров
        - Запуск ProcessingThread с сервисом
        - Блокировка кнопки до завершения обработки
        """
        files = self._get_files()
        managers = self._get_managers()

        # Проверка наличия файлов
        if not files:
            self._set_status("❌ Выберите файлы", is_error=True)
            return

        # Проверка наличия менеджеров
        if not managers:
            self._set_status("❌ Введите менеджеров", is_error=True)
            return

        # Блокировка кнопки обработки
        self._process_button.setEnabled(False)
        self._export_button.setVisible(False)

        # ✅ Запуск потока обработки с использованием сервиса (DI)
        self._processing_thread = ProcessingThread(
            service=self._service,
            file_paths=files,
            managers=managers,
            processing_settings=self._processing_settings,
            parent=self,
        )
        self.register_thread(self._processing_thread)
        self._processing_thread.finished.connect(self._on_processing_finished)
        self._processing_thread.error.connect(self._on_processing_error)
        self._processing_thread.progress.connect(self._on_processing_progress)

        self._set_status("⏳ Обработка начата...", is_error=False)
        self._processing_thread.start()

    def _on_processing_finished(self, df, stats: dict) -> None:
        """
        Обработчик завершения обработки.

        Args:
            df: DataFrame с обработанными данными
            stats: Статистика обработки
        """
        # Разблокировка кнопки
        self._process_button.setEnabled(True)

        # Сохранение данных
        self._df = df
        self._stats = stats

        # Извлечение статистики
        leads_count = len(df) if hasattr(df, "__len__") else 0
        processing_time = stats.get("processing_time_ms", 0)

        # Отображение статуса
        self._set_status(
            f"✅ Обработка завершена за {processing_time}мс: {leads_count} лидов",
            is_error=False,
        )

        # Показ кнопки экспорта
        self._export_button.setVisible(True)

        # ✅ Сохранение в БД теперь выполняет сервис
        # (вызывается в ProcessingService.process_files())

    def _on_processing_error(self, error_message: str) -> None:
        """
        Обработчик ошибки обработки.

        Args:
            error_message: Текст ошибки
        """
        self._process_button.setEnabled(True)
        self._set_status(f"❌ {error_message}", is_error=True)

    def _on_processing_progress(self, progress: int, status: str) -> None:
        """
        Обработчик прогресса обработки.

        Args:
            progress: Прогресс (0-100)
            status: Текст статуса
        """
        self._set_status(f"⏳ {status} ({progress}%)", is_error=False)

    def _on_export_clicked(self) -> None:
        """
        Обработка нажатия кнопки экспорта.

        Открывает диалог сохранения файла и запускает экспорт в CSV.
        """
        if self._df is None:
            self._set_status("❌ Нет данных для экспорта", is_error=True)
            return

        # Диалог сохранения файла
        default_filename = f"leadgen_export_{len(self._df)}_leads.csv"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл для Битрикс24", default_filename, CSV_SAVE_FILTER
        )

        if not filepath:
            return

        # Запуск потока экспорта
        self._export_button.setEnabled(False)
        self._export_thread = ExportThread(
            df=self._df,
            filepath=filepath,
            stage=self._config.get("bitrix", {}).get("stage", "Новая заявка"),
            source=self._config.get("bitrix", {}).get("source", "Холодный звонок"),
            service_type=self._config.get("bitrix", {}).get("service_type", "ГЦК"),
            parent=self,
        )
        self._export_thread.finished.connect(self._on_export_finished)
        self._export_thread.error.connect(self._on_export_error)
        self._export_thread.start()

    def _on_export_finished(self, success: bool, message: str) -> None:
        """
        Обработчик завершения экспорта.

        Args:
            success: Флаг успеха
            message: Сообщение
        """
        self._export_button.setEnabled(True)

        if success:
            self._set_status(f"✅ {message}", is_error=False)
        else:
            self._set_status(f"❌ {message}", is_error=True)

    def _on_export_error(self, error_message: str) -> None:
        """
        Обработчик ошибки экспорта.

        Args:
            error_message: Текст ошибки
        """
        self._export_button.setEnabled(True)
        self._set_status(f"❌ {error_message}", is_error=True)
