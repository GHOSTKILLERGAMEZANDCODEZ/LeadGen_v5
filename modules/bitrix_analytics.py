"""
Модуль аналитики Битрикс24.

Анализ лидов (LEAD) и сделок (DEAL) из экспорта Битрикс24.
Сопоставление по "Источнику телефона" и номеру телефона.
Извлечение категории из названия лида/сделки.
"""

import pandas as pd
import re
from typing import Dict


CSV_READ_OPTIONS = {
    "sep": ";",
    "encoding": "utf-8-sig",
    "dtype": str,
    "low_memory": False,
}
SOURCE_PHONE_COLUMN = "Источник телефона"
LEAD_PHONE_COLUMNS = ("Рабочий телефон норм", "Мобильный телефон норм")


def _read_bitrix_csv(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath, **CSV_READ_OPTIONS)


def _has_value(series: pd.Series) -> pd.Series:
    return series.notna() & (series != "")


def _collect_phone_set(row: pd.Series) -> set:
    phones = set()
    for column in LEAD_PHONE_COLUMNS:
        value = row.get(column)
        if pd.notna(value) and value:
            phones.add(value)
    return phones


def extract_category(title: str) -> str:
    """
    Извлекает категорию из названия лида/сделки.

    Формат: "Категория - Название компании" → "Категория"

    Args:
        title: Название лида или сделки

    Returns:
        Категория или исходное название если формат не распознан
    """
    if pd.isna(title) or not title:
        return ""

    # Разделяем по " - " (тире с пробелами)
    parts = str(title).split(" - ", 1)

    if len(parts) > 1:
        return parts[0].strip()

    return str(title).strip()


def normalize_phone(phone: str) -> str | None:
    """
    Нормализует телефон для сопоставления.

    Args:
        phone: Исходный телефон

    Returns:
        Нормализованный телефон (только цифры) или None
    """
    if pd.isna(phone) or not phone:
        return None

    # Удаляем все нецифровые символы
    digits = re.sub(r"\D", "", str(phone))

    # Если номер начинается с 8, заменяем на 7
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]

    # Если номер начинается с 7 и имеет 11 цифр
    if digits.startswith("7") and len(digits) == 11:
        return digits

    # Если 10 цифр (без 7)
    if len(digits) == 10:
        return "7" + digits

    return digits if len(digits) >= 10 else None


def load_lead_csv(filepath: str) -> pd.DataFrame:
    """
    Загружает LEAD.csv и обрабатывает данные.

    Args:
        filepath: Путь к файлу LEAD.csv

    Returns:
        DataFrame с обработанными лидами
    """
    # Читаем CSV с разделителем ;
    df = _read_bitrix_csv(filepath)

    # Извлекаем категорию из названия лида
    df["Категория"] = df["Название лида"].apply(extract_category)

    # Нормализуем телефоны
    df["Рабочий телефон норм"] = df["Рабочий телефон"].apply(normalize_phone)
    df["Мобильный телефон норм"] = df["Мобильный телефон"].apply(normalize_phone)

    # Создаём список всех телефонов для поиска
    df["Все телефоны"] = df.apply(_collect_phone_set, axis=1)

    # Фильтруем только лиды с "Источником телефона" (наши лиды)
    df["Наш лид"] = _has_value(df[SOURCE_PHONE_COLUMN])

    return df


def load_deal_csv(filepath: str) -> pd.DataFrame:
    """
    Загружает DEAL.csv и обрабатывает данные.

    Args:
        filepath: Путь к файлу DEAL.csv

    Returns:
        DataFrame с обработанными сделками
    """
    # Читаем CSV с разделителем ;
    df = _read_bitrix_csv(filepath)

    # Извлекаем категорию из названия сделки
    df["Категория"] = df["Название сделки"].apply(extract_category)

    # Ищем колонку с телефоном контакта (может называться по-разному)
    phone_columns = [col for col in df.columns if "Телефон" in col and "Контакт" in col]

    if phone_columns:
        # Берём первую найденную колонку с телефоном
        df["Телефон контакта"] = df[phone_columns[0]]
    else:
        df["Телефон контакта"] = None

    # Нормализуем телефон
    df["Телефон норм"] = df["Телефон контакта"].apply(normalize_phone)

    # Проверяем наличие "Источника телефона"
    df["Наша сделка"] = _has_value(df[SOURCE_PHONE_COLUMN])

    return df


def match_leads_to_deals(leads: pd.DataFrame, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Сопоставляет лиды и сделки.

    Логика:
    1. Если у сделки есть "Источник телефона" → это наша сделка
    2. Если нет → ищем лид с таким же телефоном и "Источником телефона"

    Args:
        leads: DataFrame с лидами
        deals: DataFrame со сделками

    Returns:
        DataFrame со сделками и сопоставленными лидами
    """
    deals_result = deals.copy()

    # Векторизованное создание словаря телефонов наших лидов
    our_leads_phones = {}
    leads_filtered = leads[leads["Наш лид"]].copy()

    if not leads_filtered.empty:
        # Преобразуем в формат для быстрого поиска
        for _, row in leads_filtered.iterrows():
            for phone in row["Все телефоны"]:
                if phone:  # Проверяем на пустое значение
                    if phone not in our_leads_phones:
                        our_leads_phones[phone] = []
                    our_leads_phones[phone].append(
                        {
                            "lead_id": row["ID"],
                            "category": row["Категория"],
                            "source": row["Источник телефона"],
                            "manager": row.get("Ответственный", ""),
                            "stage": row.get("Стадия", ""),
                        }
                    )

    # Векторизованное сопоставление сделок с лидами
    def find_lead_for_deal(deal_row):
        """Находит лид для сделки."""
        # Если сделка уже имеет "Источник телефона"
        if deal_row["Наша сделка"]:
            return (
                None,  # matched_lead
                deal_row["Категория"],  # matched_category
                deal_row.get("Источник телефона", ""),  # matched_source
                deal_row.get("Ответственный", ""),  # matched_manager
            )

        # Ищем по телефону
        deal_phone = deal_row["Телефон норм"]
        if deal_phone and deal_phone in our_leads_phones:
            lead_info = our_leads_phones[deal_phone][0]
            return (
                lead_info["lead_id"],
                lead_info["category"],
                lead_info["source"],
                lead_info["manager"],
            )

        return None, None, None, None

    # Применяем функцию ко всем сделкам
    results = deals_result.apply(find_lead_for_deal, axis=1, result_type="expand")
    results.columns = [
        "Сопоставленный лид",
        "Категория (из лида)",
        "Источник (из лида)",
        "Менеджер (из лида)",
    ]

    deals_result["Сопоставленный лид"] = results["Сопоставленный лид"]
    deals_result["Категория (из лида)"] = results["Категория (из лида)"]
    deals_result["Источник (из лида)"] = results["Источник (из лида)"]
    deals_result["Менеджер (из лида)"] = results["Менеджер (из лида)"]

    # Финальный флаг "Наша сделка"
    deals_result["Наша сделка"] = deals_result["Источник (из лида)"].notna()

    return deals_result


def calculate_metrics(leads: pd.DataFrame, deals: pd.DataFrame) -> Dict:
    """
    Рассчитывает метрики аналитики.

    Args:
        leads: DataFrame с лидами
        deals: DataFrame со сделками (после match_leads_to_deals)

    Returns:
        Словарь с метриками
    """
    # Фильтруем наши лиды и сделки
    our_leads = leads[leads["Наш лид"]]
    our_deals = deals[deals["Наша сделка"]]

    # Векторизованное объединение groupby операций
    metrics = {
        "total_leads": len(our_leads),
        "total_deals": len(our_deals),
        "conversion_rate": (
            len(our_deals) / len(our_leads) * 100 if len(our_leads) > 0 else 0
        ),
    }

    # Группируем один раз для всех метрик лидов
    if not our_leads.empty:
        lead_stage_agg = our_leads.groupby("Стадия").size().to_dict()
        lead_category_agg = our_leads.groupby("Категория").size().to_dict()
        lead_manager_agg = our_leads.groupby("Ответственный").size().to_dict()
        lead_refusal_agg = (
            our_leads[our_leads["Причина отказа"].notna()]
            .groupby("Причина отказа")
            .size()
            .to_dict()
        )

        metrics.update(
            {
                "lead_stages": lead_stage_agg,
                "leads_by_category": lead_category_agg,
                "leads_by_manager": lead_manager_agg,
                "lead_refusals": lead_refusal_agg,
            }
        )
    else:
        metrics.update(
            {
                "lead_stages": {},
                "leads_by_category": {},
                "leads_by_manager": {},
                "lead_refusals": {},
            }
        )

    # Группируем один раз для всех метрик сделок
    if not our_deals.empty:
        deal_stage_agg = our_deals.groupby("Стадия сделки").size().to_dict()
        deal_category_agg = our_deals.groupby("Категория (из лида)").size().to_dict()
        deal_manager_agg = our_deals.groupby("Менеджер (из лида)").size().to_dict()
        deal_refusal_agg = (
            our_deals[our_deals["Причина отказа"].notna()]
            .groupby("Причина отказа")
            .size()
            .to_dict()
        )

        metrics.update(
            {
                "deal_stages": deal_stage_agg,
                "deals_by_category": deal_category_agg,
                "deals_by_manager": deal_manager_agg,
                "deal_refusals": deal_refusal_agg,
            }
        )
    else:
        metrics.update(
            {
                "deal_stages": {},
                "deals_by_category": {},
                "deals_by_manager": {},
                "deal_refusals": {},
            }
        )

    # Конверсия по категориям
    metrics["conversion_by_category"] = {}
    all_categories = set(metrics.get("leads_by_category", {}).keys()) | set(
        metrics.get("deals_by_category", {}).keys()
    )
    for category in all_categories:
        leads_count = metrics["leads_by_category"].get(category, 0)
        deals_count = metrics["deals_by_category"].get(category, 0)
        metrics["conversion_by_category"][category] = {
            "leads": leads_count,
            "deals": deals_count,
            "conversion": deals_count / leads_count * 100 if leads_count > 0 else 0,
        }

    # Конверсия по менеджерам
    metrics["conversion_by_manager"] = {}
    all_managers = set(metrics.get("leads_by_manager", {}).keys()) | set(
        metrics.get("deals_by_manager", {}).keys()
    )
    for manager in all_managers:
        if manager:
            leads_count = metrics["leads_by_manager"].get(manager, 0)
            deals_count = metrics["deals_by_manager"].get(manager, 0)
            metrics["conversion_by_manager"][manager] = {
                "leads": leads_count,
                "deals": deals_count,
                "conversion": deals_count / leads_count * 100 if leads_count > 0 else 0,
            }

    return metrics


def analyze_bitrix(
    lead_filepath: str, deal_filepath: str
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Полный цикл анализа Битрикс24.

    Args:
        lead_filepath: Путь к LEAD.csv
        deal_filepath: Путь к DEAL.csv

    Returns:
        Кортеж (leads_df, deals_df, metrics)
    """
    # Загружаем данные
    leads = load_lead_csv(lead_filepath)
    deals = load_deal_csv(deal_filepath)

    # Сопоставляем лиды и сделки
    deals_matched = match_leads_to_deals(leads, deals)

    # Рассчитываем метрики
    metrics = calculate_metrics(leads, deals_matched)

    return leads, deals_matched, metrics
