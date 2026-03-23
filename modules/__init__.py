"""
Бизнес-логика проекта.
"""

from .services import ProcessingService
from .phone_validator import clean_phone, validate_phone, extract_phone_from_any
from .data_processor import (
    SecurityError,
    is_safe_path,
    load_file,
    process_file,
    merge_files,
    remove_duplicates,
    assign_managers,
    get_preview_data,
)
from .bitrix_mapper import map_to_bitrix, export_to_bitrix_csv, get_bitrix_columns
from .exceptions import (
    LeadGenError,
    SecurityError as LeadGenSecurityError,
    BitrixWebhookError,
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookInvalidURLError,
    BitrixWebhookConnectionError,
    ProcessingError,
    ValidationError,
    ExportError,
)
from .bitrix_analytics import (
    analyze_bitrix,
    load_lead_csv,
    load_deal_csv,
    match_leads_to_deals,
    calculate_metrics,
    extract_category,
    normalize_phone,
)
from .chart_generator import (
    create_pie_chart,
    create_bar_chart,
    create_funnel_chart,
    create_conversion_chart,
    create_manager_performance_chart,
)
from .report_exporter import create_analytics_report
from .lpr_parser import (
    parse_html_content,
    save_lpr_to_csv,
    load_companies_from_csv,
    extract_fio,
    extract_position,
    extract_inn,
)

__all__ = [
    # Сервисы
    "ProcessingService",
    # Исключения
    "SecurityError",
    "LeadGenSecurityError",
    "LeadGenError",
    "BitrixWebhookError",
    "BitrixWebhookNotFoundError",
    "BitrixWebhookForbiddenError",
    "BitrixWebhookRateLimitError",
    "BitrixWebhookInvalidURLError",
    "BitrixWebhookConnectionError",
    "ProcessingError",
    "ValidationError",
    "ExportError",
    # Валидация телефонов
    "clean_phone",
    "validate_phone",
    "extract_phone_from_any",
    # Обработка данных
    "is_safe_path",
    "load_file",
    "process_file",
    "merge_files",
    "remove_duplicates",
    "assign_managers",
    "get_preview_data",
    # Битрикс24 маппинг
    "map_to_bitrix",
    "export_to_bitrix_csv",
    "get_bitrix_columns",
    # Битрикс24 аналитика
    "analyze_bitrix",
    "load_lead_csv",
    "load_deal_csv",
    "match_leads_to_deals",
    "calculate_metrics",
    "extract_category",
    "normalize_phone",
    # Графики
    "create_pie_chart",
    "create_bar_chart",
    "create_funnel_chart",
    "create_conversion_chart",
    "create_manager_performance_chart",
    # Отчёты
    "create_analytics_report",
    # Парсинг ЛПР
    "parse_html_content",
    "save_lpr_to_csv",
    "load_companies_from_csv",
    "extract_fio",
    "extract_position",
    "extract_inn",
]
