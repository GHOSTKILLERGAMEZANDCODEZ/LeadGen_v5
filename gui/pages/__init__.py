"""
Модуль страниц приложения LeadGen v5.

Предоставляет компоненты страниц для навигации в GUI приложении.
"""

from .home_page import HomePage
from .processing_page import ProcessingPage
from .analytics_page import AnalyticsPage
from .link_generator_page import LinkGeneratorPage
from .lpr_finder_page import LPRFinderPage
from .manager_monitor_page import ManagerMonitorPage
from .settings_page import SettingsPage

__all__ = [
    "HomePage",
    "ProcessingPage",
    "AnalyticsPage",
    "LinkGeneratorPage",
    "LPRFinderPage",
    "ManagerMonitorPage",
    "SettingsPage",
]
