"""
Модуль маппинга данных для импорта в Битрикс24.

Формирует CSV согласно шаблону lead.csv (64 колонки, разделитель ;).
"""

import logging
from collections.abc import Callable
import pandas as pd

# Настраиваем логгер
logger = logging.getLogger("bitrix_mapper")

# Константы
BITRIX_COLUMN_COUNT = 64  # Количество колонок в шаблоне Битрикс24
CSV_SEPARATOR = ";"  # Разделитель для CSV
CSV_ENCODING = "utf-8-sig"  # Кодировка UTF-8 с BOM для Excel
DEFAULT_STAGE = "Новая заявка"
DEFAULT_SOURCE = "Холодный звонок"
DEFAULT_SERVICE_TYPE = "ГЦК"
_EMPTY_VALUE_KEYS = {"nan", "none", ""}
_HTTP_PREFIXES = ("https://", "http://")

# Импорт с валидацией и fallback
try:
    from ..utils.url_cleaner import clean_url
except ImportError:
    try:
        from utils.url_cleaner import clean_url
    except ImportError:

        def clean_url(url: str) -> str:
            """Fallback URL cleaner - removes UTM parameters."""
            if not url or url.lower() in ("none", "nan", ""):
                return ""
            # Simple fallback - just return URL as-is
            logger.warning("url_cleaner not found, using fallback")
            return str(url)


# Колонки согласно шаблону lead.csv (64 колонки)
BITRIX_COLUMNS = [
    "ID",
    "Название лида",
    "Обращение",
    "Имя",
    "Фамилия",
    "Отчество",
    "Имя, Фамилия",
    "Дата рождения",
    "Адрес",
    "Улица, номер дома",
    "Квартира, офис, комната, этаж",
    "Населенный пункт",
    "Район",
    "Регион",
    "Почтовый индекс",
    "Страна",
    "Рабочий телефон",
    "Мобильный телефон",
    "Номер факса",
    "Домашний телефон",
    "Номер пейджера",
    "Телефон для рассылок",
    "Другой телефон",
    "Корпоративный сайт",
    "Личная страница",
    "Страница Facebook",
    "Страница ВКонтакте",
    "Страница LiveJournal",
    "Микроблог Twitter",
    "Другой сайт",
    "Рабочий e-mail",
    "Частный e-mail",
    "E-mail для рассылок",
    "Другой e-mail",
    "Контакт Facebook",
    "Контакт Telegram",
    "Контакт ВКонтакте",
    "Контакт Viber",
    "Комментарии Instagram",
    "Контакт Битрикс24 Network",
    "Онлайн-чат",
    "Контакт Открытая линия",
    "Другой контакт",
    "Связанный пользователь",
    "Название компании",
    "Должность",
    "Комментарий",
    "Стадия",
    "Дополнительно о стадии",
    "Товар",
    "Цена",
    "Количество",
    "Возможная сумма",
    "Валюта",
    "Источник",
    "Дополнительно об источнике",
    "Доступен для всех",
    "Ответственный",
    "Тип услуги",
    "Новый файл",
    "Доп файл",
    "Источник телефона",
    "Причина отказа",
    "дело",
]


def _clean_string_series(series: pd.Series) -> pd.Series:
    cleaned = series.fillna("").astype(str).str.strip()
    lowered = cleaned.str.lower()
    return cleaned.mask(lowered.isin(_EMPTY_VALUE_KEYS), "")


def _strip_url_prefixes(series: pd.Series) -> pd.Series:
    cleaned = _clean_string_series(series)
    for prefix in _HTTP_PREFIXES:
        cleaned = cleaned.str.replace(prefix, "", regex=False)
    return cleaned


def _clean_telegram_series(series: pd.Series) -> pd.Series:
    cleaned = _strip_url_prefixes(series)
    cleaned = cleaned.str.replace("t.me/", "", regex=False)
    cleaned = cleaned.str.replace("@", "", regex=False)
    cleaned = cleaned.str.split("/").str[0]
    return cleaned.where(cleaned == "", "@" + cleaned)


def _clean_vk_series(series: pd.Series) -> pd.Series:
    cleaned = _strip_url_prefixes(series)
    cleaned = cleaned.str.replace("vk.com/", "", regex=False)
    cleaned = cleaned.str.replace("@", "", regex=False)
    return cleaned.str.split("/").str[0]


def _clean_url_series(series: pd.Series) -> pd.Series:
    cleaned = _clean_string_series(series)
    return cleaned.apply(clean_url)


def _has_value(series: pd.Series) -> pd.Series:
    cleaned = _clean_string_series(series)
    return cleaned != ""


def _set_if_present(
    result: pd.DataFrame,
    df: pd.DataFrame,
    source_column: str,
    target_column: str | None = None,
    transform: Callable[[pd.Series], pd.Series] | None = None,
) -> None:
    if source_column not in df.columns:
        return
    series = df[source_column]
    if transform is not None:
        series = transform(series)
    else:
        series = _clean_string_series(series)
    result[target_column or source_column] = series


def map_to_bitrix(
    df: pd.DataFrame,
    stage: str = DEFAULT_STAGE,
    source: str = DEFAULT_SOURCE,
    service_type: str = DEFAULT_SERVICE_TYPE,
    lpr_column: str | None = None,  # Колонка с данными ЛПР
) -> pd.DataFrame:
    """
    Преобразует DataFrame в формат для импорта в Битрикс24 согласно шаблону lead.csv.

    Args:
        df: DataFrame с обработанными данными
        stage: Стадия лида
        source: Источник
        service_type: Тип услуги
        lpr_column: Название колонки с данными ЛПР (для добавления в Комментарий)
    """
    result = pd.DataFrame("", columns=BITRIX_COLUMNS, index=range(len(df)))

    # Название лида: [Category 0] - [Название]
    if "Название лида" in df.columns:
        result["Название лида"] = _clean_string_series(df["Название лида"])
    elif "Название компании" in df.columns:
        result["Название лида"] = _clean_string_series(df["Название компании"])

    # Название компании
    _set_if_present(result, df, "Название компании")

    # Рабочий телефон
    _set_if_present(result, df, "Рабочий телефон")

    # Мобильный телефон
    _set_if_present(result, df, "Мобильный телефон")

    # Адрес
    _set_if_present(result, df, "Адрес")

    # Сайт (очищаем от UTM-меток)
    _set_if_present(
        result, df, "Корпоративный сайт", transform=_clean_url_series
    )

    # Telegram (username) - векторизованная версия
    _set_if_present(
        result, df, "Контакт Telegram", transform=_clean_telegram_series
    )

    # ВКонтакте (username) - векторизованная версия
    if "Контакт ВКонтакте" in df.columns:
        result["Страница ВКонтакте"] = _clean_vk_series(df["Контакт ВКонтакте"])

    # Стадия
    result["Стадия"] = stage

    # Источник
    result["Источник"] = source

    # Доступен для всех
    result["Доступен для всех"] = "да"

    # Ответственный
    _set_if_present(result, df, "Ответственный")

    # Тип услуги
    result["Тип услуги"] = service_type

    # Источник телефона (отдельная колонка)
    _set_if_present(result, df, "Источник телефона")

    # Комментарий
    comment_series = pd.Series("", index=df.index)
    if lpr_column and lpr_column in df.columns:
        lpr_data = _clean_string_series(df[lpr_column])
        comment_series = lpr_data.where(lpr_data == "", "ЛПР: " + lpr_data)
    result["Комментарий"] = comment_series

    # Удаляем пустые строки (где нет названия, телефона, адреса)
    # Оставляем строки где есть хотя бы одно из: Название лида, Рабочий телефон, Мобильный телефон, Адрес, Название компании
    mask = (
        _has_value(result["Название лида"])
        | _has_value(result["Рабочий телефон"])
        | _has_value(result["Мобильный телефон"])
        | _has_value(result["Адрес"])
        | _has_value(result["Название компании"])
    )
    result = result[mask].reset_index(drop=True)

    return result


def export_to_bitrix_csv(
    df: pd.DataFrame,
    filepath: str,
    stage: str = DEFAULT_STAGE,
    source: str = DEFAULT_SOURCE,
    service_type: str = DEFAULT_SERVICE_TYPE,
    lpr_column: str | None = None,
) -> bool:
    """
    Экспортирует DataFrame в CSV файл для импорта в Битрикс24.

    Используется разделитель ; (точка с запятой) согласно шаблону.

    Args:
        df: DataFrame с обработанными данными
        filepath: Путь для сохранения файла
        stage: Стадия лида
        source: Источник
        service_type: Тип услуги
        lpr_column: Название колонки с данными ЛПР
    """
    try:
        bitrix_df = map_to_bitrix(df, stage, source, service_type, lpr_column)

        # Экспорт с разделителем ; согласно шаблону
        bitrix_df.to_csv(
            filepath,
            sep=CSV_SEPARATOR,
            encoding=CSV_ENCODING,  # UTF-8 с BOM для Excel
            index=False,
            quoting=1,  # QUOTE_ALL — кавычки вокруг всех полей
        )

        logger.info(
            f"Экспорт в Битрикс CSV выполнен: {filepath} ({len(bitrix_df)} лидов)"
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка экспорта в Битрикс CSV: {e}", exc_info=True)
        return False


def get_bitrix_columns() -> list[str]:
    """Возвращает список колонок Битрикс24 согласно шаблону."""
    return BITRIX_COLUMNS.copy()
