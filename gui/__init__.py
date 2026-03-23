"""
GUI модуль приложения LeadGen v5 на PySide6.
"""

from gui.main_window import MainWindow
from gui.sidebar import Sidebar
from gui.components.file_loader import FileLoaderWidget
from gui.components.file_list import FileListWidget
from gui.components.circular_progress import CircularProgress
from gui.pages.home_page import HomePage
from gui.pages.processing_page import ProcessingPage
from gui.pages.analytics_page import AnalyticsPage
from gui.pages.link_generator_page import LinkGeneratorPage
from gui.pages.lpr_finder_page import LPRFinderPage
from gui.pages.manager_monitor_page import ManagerMonitorPage
from gui.pages.settings_page import SettingsPage
from gui.styles.stylesheet import get_main_stylesheet
from gui.styles.theme import (
    BACKGROUND_PRIMARY,
    BACKGROUND_SECONDARY,
    ACCENT_CYAN,
    TEXT_PRIMARY,
)

__all__ = [
    # Main window
    "MainWindow",
    # Components
    "Sidebar",
    "FileLoaderWidget",
    "FileListWidget",
    "CircularProgress",
    # Pages
    "HomePage",
    "ProcessingPage",
    "AnalyticsPage",
    "LinkGeneratorPage",
    "LPRFinderPage",
    "ManagerMonitorPage",
    "SettingsPage",
    # Styles
    "get_main_stylesheet",
    "BACKGROUND_PRIMARY",
    "BACKGROUND_SECONDARY",
    "ACCENT_CYAN",
    "TEXT_PRIMARY",
]
