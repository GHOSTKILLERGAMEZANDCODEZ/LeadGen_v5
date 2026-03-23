"""Конфигурация pytest для GUI тестов."""

import pytest
from PySide6.QtWidgets import QApplication
import sys


@pytest.fixture(scope="session")
def qapp():
    """Создаёт QApplication для сессии тестов."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Не закрываем приложение после тестов


@pytest.fixture
def qtbot(qtbot):
    """Расширяет стандартный qtbot для GUI тестов."""
    yield qtbot
