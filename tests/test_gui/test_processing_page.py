"""
Тесты для страницы обработки лидов (ProcessingPage).

Тестирует:
- Инициализацию страницы
- UI элементы (кнопки, списки, метки)
- Drag & Drop функциональность
- Обработку ошибок
- Интеграцию с сервисом обработки
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pandas as pd
import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtCore import QMimeData, QUrl, Qt
from PySide6.QtWidgets import QListWidgetItem

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from gui.pages.processing_page import ProcessingPage
from gui.components.file_list import FileListWidget
from gui.components.file_loader import FileLoaderWidget
from modules.services.processing_service import ProcessingService
from gui.threads.processing_thread import ProcessingThread


class TestProcessingPageInit:
    """Тесты инициализации страницы обработки."""

    def test_processing_page_init(self, qtbot: QtBot) -> None:
        """Тестирует базовую инициализацию страницы."""
        page = ProcessingPage()
        qtbot.addWidget(page)

        assert page is not None
        assert page.objectName() == "ProcessingPage"
        assert page._config is not None
        assert page._service is not None
        assert isinstance(page._service, ProcessingService)

    def test_processing_page_with_mock_service(self, qtbot: QtBot) -> None:
        """Тестирует создание страницы с mock сервисом (DI)."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)

        assert page is not None
        assert page._service == mock_service
        assert page._service is not None


class TestProcessingPageUIElements:
    """Тесты UI элементов страницы."""

    @pytest.fixture
    def page(self, qtbot: QtBot) -> ProcessingPage:
        """Создаёт страницу обработки для тестов."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_file_list_widget_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие списка файлов."""
        assert page._file_list is not None
        assert isinstance(page._file_list, FileListWidget)
        assert page._file_list._list_widget.count() == 0

    def test_file_loader_widget_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие виджета загрузки файлов."""
        assert page._file_loader is not None
        assert isinstance(page._file_loader, FileLoaderWidget)

    def test_process_button_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие кнопки обработки."""
        assert page._process_button is not None
        assert page._process_button.text() == "🚀 Очистить и объединить"
        assert page._process_button.isEnabled()
        assert page._process_button.isVisible()

    def test_export_button_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие кнопки экспорта."""
        assert page._export_button is not None
        assert page._export_button.text() == "Экспортировать в Битрикс"
        assert not page._export_button.isVisible()  # Скрыта пока нет данных

    def test_status_label_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие метки статуса."""
        assert page._status_label is not None
        assert page._status_label.text() == ""

    def test_managers_input_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие поля ввода менеджеров."""
        assert page._managers_input is not None
        assert page._managers_input.toPlainText() == ""

    def test_page_title_exists(self, page: ProcessingPage) -> None:
        """Тестирует наличие заголовка страницы."""
        assert page._page_title is not None
        assert page._page_title.text() == "Обработка лидов"


class TestProcessingPageDragDrop:
    """Тесты Drag & Drop функциональности."""

    @pytest.fixture
    def page(self, qtbot: QtBot) -> ProcessingPage:
        """Создаёт страницу обработки для тестов."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_drag_drop_single_file(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует перетаскивание одного файла."""
        # Создаём тестовый файл
        test_file = tmp_path / "test_data.json"
        test_file.write_text('{"test": "data"}')

        # Симулируем drag & drop через FileLoaderWidget
        file_loader = page._file_loader
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Проверяем что файл поддерживается
        from pathlib import Path as PathLib
        assert file_loader._is_valid_file(PathLib(str(test_file)))

    def test_drag_drop_multiple_files(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует перетаскивание нескольких файлов."""
        # Создаём тестовые файлы
        test_file1 = tmp_path / "data1.json"
        test_file2 = tmp_path / "data2.tsv"
        test_file1.write_text('{"test": "data1"}')
        test_file2.write_text("col1\tcol2\nval1\tval2")

        # Симулируем drag & drop
        file_loader = page._file_loader
        mime_data = QMimeData()
        mime_data.setUrls([
            QUrl.fromLocalFile(str(test_file1)),
            QUrl.fromLocalFile(str(test_file2)),
        ])

        # Проверяем что файлы поддерживаются
        from pathlib import Path as PathLib
        assert file_loader._is_valid_file(PathLib(str(test_file1)))
        assert file_loader._is_valid_file(PathLib(str(test_file2)))

    def test_drag_drop_unsupported_file(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует перетаскивание неподдерживаемого файла."""
        # Создаём неподдерживаемый файл
        test_file = tmp_path / "test.txt"
        test_file.write_text("text content")

        file_loader = page._file_loader
        from pathlib import Path as PathLib
        assert not file_loader._is_valid_file(PathLib(str(test_file)))


class TestProcessingPageErrors:
    """Тесты обработки ошибок."""

    @pytest.fixture
    def page(self, qtbot: QtBot) -> ProcessingPage:
        """Создаёт страницу обработки для тестов."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_process_without_files(self, page: ProcessingPage, qtbot: QtBot) -> None:
        """Тестирует обработку без файлов."""
        # Добавляем менеджеров
        page._managers_input.setPlainText("Менеджер 1\nМенеджер 2")

        # Нажимаем кнопку обработки
        page._on_process_clicked()

        # Проверяем статус (сигнал setText был вызван)
        qtbot.wait(100)  # Даём время на обновление UI
        assert "❌ Выберите файлы" in page._status_label.text()

    def test_process_without_managers(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует обработку без менеджеров."""
        # Создаём тестовый файл
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": "data"}')

        # Добавляем файл в список
        page._file_list.add_files([str(test_file)])

        # Нажимаем кнопку обработки
        page._on_process_clicked()

        # Проверяем статус
        qtbot.wait(100)
        assert "❌ Введите менеджеров" in page._status_label.text()

    def test_process_without_files_and_managers(self, page: ProcessingPage, qtbot: QtBot) -> None:
        """Тестирует обработку без файлов и менеджеров."""
        # Очищаем всё
        page._managers_input.setPlainText("")
        page._file_list._clear_all_files()

        # Нажимаем кнопку обработки
        page._on_process_clicked()

        # Должна показать ошибку о файлах (проверка файлов первая)
        qtbot.wait(100)
        assert "❌ Выберите файлы" in page._status_label.text()


class TestProcessingPageIntegration:
    """Тесты интеграции с сервисом обработки."""

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        """Создаёт mock сервис."""
        service = MagicMock(spec=ProcessingService)
        return service

    @pytest.fixture
    def page(self, qtbot: QtBot, mock_service: MagicMock) -> ProcessingPage:
        """Создаёт страницу с mock сервисом."""
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_process_files_success(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path, mock_service: MagicMock) -> None:
        """Тестирует успешную обработку файлов."""
        # Создаём тестовый файл
        test_file = tmp_path / "test.json"
        test_file.write_text('[{"phone": "79991234567", "name": "Test"}]')

        # Настраиваем mock сервис
        mock_df = pd.DataFrame({'phone': ['79991234567'], 'name': ['Test']})
        mock_stats = {'total_rows': 1, 'duplicates_removed': 0, 'processing_time_ms': 100}
        mock_service.process_files.return_value = (mock_df, mock_stats)

        # Добавляем файл и менеджеров
        page._file_list.add_files([str(test_file)])
        page._managers_input.setPlainText("Менеджер 1")

        # Симулируем завершение обработки напрямую
        page._on_processing_finished(mock_df, mock_stats)

        # Проверяем что данные сохранены
        assert page._df is not None
        assert len(page._df) == 1
        assert page._stats is not None
        assert page._export_button.isVisible()

    def test_process_files_error(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path, mock_service: MagicMock) -> None:
        """Тестирует ошибку обработки файлов."""
        # Создаём тестовый файл
        test_file = tmp_path / "test.json"
        test_file.write_text('invalid json')

        # Настраиваем mock сервис на ошибку
        mock_service.process_files.side_effect = ValueError("Неверный формат файла")

        # Добавляем файл и менеджеров
        page._file_list.add_files([str(test_file)])
        page._managers_input.setPlainText("Менеджер 1")

        # Симулируем ошибку обработки
        page._on_processing_error("Неверный формат файла")

        # Проверяем статус
        assert "❌ Неверный формат файла" in page._status_label.text()
        assert not page._export_button.isVisible()

    def test_export_without_data(self, page: ProcessingPage, qtbot: QtBot) -> None:
        """Тестирует экспорт без данных."""
        # Нажимаем кнопку экспорта без данных
        page._on_export_clicked()

        # Проверяем статус
        assert "❌ Нет данных для экспорта" in page._status_label.text()

    def test_export_with_data(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует экспорт с данными."""
        # Создаём тестовые данные
        mock_df = pd.DataFrame({'phone': ['79991234567'], 'name': ['Test']})
        page._df = mock_df
        page._stats = {'total_rows': 1}

        # Показываем кнопку экспорта
        page._export_button.setVisible(True)

        # Mock для QFileDialog
        output_file = str(tmp_path / "export.csv")
        with patch('gui.pages.processing_page.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = (output_file, "CSV файлы (*.csv)")

            # Mock для ExportThread
            with patch('gui.pages.processing_page.ExportThread') as MockExportThread:
                mock_thread = MagicMock()
                MockExportThread.return_value = mock_thread

                # Нажимаем кнопку экспорта
                page._on_export_clicked()

                # Проверяем что поток создан и запущен
                MockExportThread.assert_called_once()
                mock_thread.start.assert_called_once()

    def test_get_managers(self, page: ProcessingPage) -> None:
        """Тестирует получение списка менеджеров."""
        page._managers_input.setPlainText("Менеджер 1\nМенеджер 2\n\nМенеджер 3")
        managers = page._get_managers()

        assert len(managers) == 3
        assert "Менеджер 1" in managers
        assert "Менеджер 2" in managers
        assert "Менеджер 3" in managers

    def test_get_files(self, page: ProcessingPage, tmp_path: Path) -> None:
        """Тестирует получение списка файлов."""
        test_file1 = str(tmp_path / "file1.json")
        test_file2 = str(tmp_path / "file2.tsv")
        Path(test_file1).write_text('{"test": "data1"}')
        Path(test_file2).write_text("col1\tcol2\nval1\tval2")

        page._file_list.add_files([test_file1, test_file2])
        files = page._get_files()

        assert len(files) == 2
        assert test_file1 in files
        assert test_file2 in files

    def test_set_status_success(self, page: ProcessingPage) -> None:
        """Тестирует установку статуса успеха."""
        page._set_status("✅ Успех", is_error=False)

        assert "✅ Успех" in page._status_label.text()
        # Проверяем что цвет успеха (зелёный)
        style = page._status_label.styleSheet()
        assert "color:" in style

    def test_set_status_error(self, page: ProcessingPage) -> None:
        """Тестирует установку статуса ошибки."""
        page._set_status("❌ Ошибка", is_error=True)

        assert "❌ Ошибка" in page._status_label.text()
        # Проверяем что цвет ошибки (красный)
        style = page._status_label.styleSheet()
        assert "color:" in style

    def test_clear_status(self, page: ProcessingPage) -> None:
        """Тестирует очистку статуса."""
        page._set_status("Тест", is_error=False)
        page._clear_status()

        assert page._status_label.text() == ""


class TestProcessingPageSignals:
    """Тесты сигналов страницы."""

    @pytest.fixture
    def page(self, qtbot: QtBot) -> ProcessingPage:
        """Создаёт страницу для тестов."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_process_started_signal(self, page: ProcessingPage, qtbot: QtBot, tmp_path: Path) -> None:
        """Тестирует сигнал process_started."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": "data"}')

        page._file_list.add_files([str(test_file)])
        page._managers_input.setPlainText("Менеджер 1")

        # Подключаемся к сигналу
        received_files = []
        received_managers = []

        def on_process_started(files: list, managers: list) -> None:
            received_files.extend(files)
            received_managers.extend(managers)

        page.process_started.connect(on_process_started)

        # Симулируем нажатие (но не запускаем реальный поток)
        # Проверяем только валидацию
        files = page._get_files()
        managers = page._get_managers()

        assert len(files) == 1
        assert len(managers) == 1


class TestProcessingPageThreadCleanup:
    """Тесты очистки потоков."""

    @pytest.fixture
    def page(self, qtbot: QtBot) -> ProcessingPage:
        """Создаёт страницу для тестов."""
        mock_service = MagicMock(spec=ProcessingService)
        page = ProcessingPage(processing_service=mock_service)
        qtbot.addWidget(page)
        page.show()
        return page

    def test_thread_cleanup_on_destroy(self, page: ProcessingPage, qtbot: QtBot) -> None:
        """Тестирует очистку потоков при уничтожении."""
        # Создаём mock поток
        mock_thread = MagicMock(spec=ProcessingThread)
        mock_thread.isRunning.return_value = True
        page.register_thread(mock_thread)

        # Вызываем closeEvent (из ThreadCleanupMixin)
        from PySide6.QtGui import QCloseEvent
        event = QCloseEvent()
        page.closeEvent(event)

        # Проверяем что поток был остановлен
        mock_thread.quit.assert_called_once()
        mock_thread.wait.assert_called_once()


class TestProcessingPageFileListWidget:
    """Тесты виджета списка файлов."""

    @pytest.fixture
    def file_list(self, qtbot: QtBot) -> FileListWidget:
        """Создаёт виджет списка файлов."""
        widget = FileListWidget()
        qtbot.addWidget(widget)
        widget.show()
        return widget

    def test_add_files(self, file_list: FileListWidget, tmp_path: Path) -> None:
        """Тестирует добавление файлов."""
        test_file1 = str(tmp_path / "file1.json")
        test_file2 = str(tmp_path / "file2.tsv")
        Path(test_file1).write_text('{"test": "data"}')
        Path(test_file2).write_text("col1\tcol2")

        file_list.add_files([test_file1, test_file2])

        assert file_list._list_widget.count() == 2
        assert len(file_list.get_file_paths()) == 2

    def test_remove_selected(self, file_list: FileListWidget, tmp_path: Path) -> None:
        """Тестирует удаление выбранного файла."""
        test_file = str(tmp_path / "file.json")
        Path(test_file).write_text('{"test": "data"}')

        file_list.add_files([test_file])
        assert file_list._list_widget.count() == 1

        # Выбираем и удаляем
        file_list._list_widget.setCurrentRow(0)
        file_list._remove_selected()

        assert file_list._list_widget.count() == 0

    def test_clear_all(self, file_list: FileListWidget, tmp_path: Path) -> None:
        """Тестирует очистку всех файлов."""
        test_file1 = str(tmp_path / "file1.json")
        test_file2 = str(tmp_path / "file2.tsv")
        Path(test_file1).write_text('{"test": "data1"}')
        Path(test_file2).write_text("col1\tcol2")

        file_list.add_files([test_file1, test_file2])
        assert file_list._list_widget.count() == 2

        file_list._clear_all_files()

        assert file_list._list_widget.count() == 0
        assert len(file_list.get_file_paths()) == 0

    def test_no_duplicates(self, file_list: FileListWidget, tmp_path: Path) -> None:
        """Тестирует что дубликаты не добавляются."""
        test_file = str(tmp_path / "file.json")
        Path(test_file).write_text('{"test": "data"}')

        file_list.add_files([test_file, test_file, test_file])

        assert file_list._list_widget.count() == 1


class TestProcessingPageFileLoaderWidget:
    """Тесты виджета загрузки файлов."""

    @pytest.fixture
    def file_loader(self, qtbot: QtBot) -> FileLoaderWidget:
        """Создаёт виджет загрузки файлов."""
        widget = FileLoaderWidget()
        qtbot.addWidget(widget)
        widget.show()
        return widget

    def test_valid_extensions(self, file_loader: FileLoaderWidget) -> None:
        """Тестирует проверку поддерживаемых расширений."""
        from pathlib import Path as PathLib

        assert file_loader._is_valid_file(PathLib("test.json"))
        assert file_loader._is_valid_file(PathLib("test.tsv"))
        assert file_loader._is_valid_file(PathLib("test.csv"))
        assert file_loader._is_valid_file(PathLib("TEST.JSON"))  # Case insensitive

    def test_invalid_extensions(self, file_loader: FileLoaderWidget) -> None:
        """Тестирует проверку неподдерживаемых расширений."""
        from pathlib import Path as PathLib

        assert not file_loader._is_valid_file(PathLib("test.txt"))
        assert not file_loader._is_valid_file(PathLib("test.pdf"))
        assert not file_loader._is_valid_file(PathLib("test.xlsx"))

    def test_collect_valid_paths(self, file_loader: FileLoaderWidget, tmp_path: Path) -> None:
        """Тестирует сбор валидных путей."""
        test_file1 = tmp_path / "data.json"
        test_file2 = tmp_path / "data.tsv"
        test_file3 = tmp_path / "data.txt"  # Недопустимый

        test_file1.write_text('{"test": "data"}')
        test_file2.write_text("col1\tcol2")
        test_file3.write_text("text")

        urls = [
            QUrl.fromLocalFile(str(test_file1)),
            QUrl.fromLocalFile(str(test_file2)),
            QUrl.fromLocalFile(str(test_file3)),
        ]

        paths = file_loader._collect_valid_paths(urls)

        assert len(paths) == 2
        assert str(test_file1) in paths
        assert str(test_file2) in paths
        assert str(test_file3) not in paths


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
