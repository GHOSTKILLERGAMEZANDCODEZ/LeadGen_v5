"""
Lead Generation Automation System
Точка входа приложения на PySide6.
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.main_window import MainWindow
from utils.logger import setup_logger
from core.dependency_container import DependencyContainer


def main():
    """Точка входа в приложение."""
    logger = setup_logger('leadgen_main')
    logger.info("Запуск LeadGen v5 (PySide6)")

    # DependencyContainer
    container = DependencyContainer()
    logger.info("DependencyContainer инициализирован")

    # High DPI (должно быть ДО создания QApplication)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("LeadGen v5")
    app.setOrganizationName("DIRECT-LINE")

    # Шрифт
    font = QFont("Inter", 13)
    app.setFont(font)

    # Окно с DI
    window = MainWindow(container=container)
    window.show()

    logger.info("Главное окно отображено")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
