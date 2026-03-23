"""
Модуль обработки данных: загрузка, очистка и объединение CSV/TSV/JSON файлов.

Функции:
- Загрузка TSV/CSV/JSON файлов от Webbee AI
- Очистка данных (телефоны, удаление лишних колонок)
- Удаление дубликатов по номерам телефонов
- Добавление источника телефона
- Распределение по менеджерам (round-robin)
"""

import os
import json
import logging
from pathlib import Path
import pandas as pd

# Настраиваем логгер
logger = logging.getLogger("data_processor")

try:
    from .phone_validator import clean_phone
except ImportError:
    from phone_validator import clean_phone


class SecurityError(Exception):
    """Исключение безопасности."""
    pass


# Разрешённые директории для загрузки файлов
ALLOWED_INPUT_DIRS = [
    Path(__file__).parent.parent / "data" / "input",
    Path(__file__).parent.parent / "UPLOAD",
    Path.home() / "Downloads",  # Папка загрузок пользователя
]


def is_safe_path(filepath: str) -> bool:
    """
    Проверяет, что путь находится в разрешённых директориях.
    
    Защита от Path Traversal атак:
    - Блокировка UNC путей (\\\\server\\share)
    - Блокировка symlink
    - Проверка через relative_to вместо строкового сравнения

    Args:
        filepath: Путь к файлу для проверки

    Returns:
        True если путь безопасен, False иначе
        
    Raises:
        SecurityError: Если путь содержит недопустимые символы
    """
    try:
        # Проверяем на недопустимые символы
        if any(char in filepath for char in '<>"|?*'):
            logger.warning(f"Путь содержит недопустимые символы: {filepath}")
            return False
        
        # Блокируем UNC пути и symlink
        if filepath.startswith('\\\\') or filepath.startswith('//'):
            logger.warning(f"Блокирован UNC путь: {filepath}")
            return False
        
        # Проверяем существование файла перед resolve
        file_path = Path(filepath)
        if not file_path.exists():
            logger.warning(f"Файл не существует: {filepath}")
            return False
        
        abs_path = file_path.resolve(strict=True)
        
        # Проверяем, что путь внутри разрешённой директории
        for allowed_dir in ALLOWED_INPUT_DIRS:
            allowed_resolved = allowed_dir.resolve(strict=True)
            try:
                # relative_to выбрасывает ValueError если путь не внутри
                abs_path.relative_to(allowed_resolved)
                return True
            except ValueError:
                continue
        
        logger.warning(f"Попытка доступа к запрещённому пути: {filepath}")
        return False
    except OSError as e:
        logger.error(f"Ошибка проверки пути {filepath}: {e}")
        return False


# Ключевые колонки из Webbee AI (JSON формат)
KEY_COLUMNS_JSON = {
    "Название": "title",
    "Адрес": "address",
    "phone_1": "phone_1",
    "phone_2": "phone_2",
    "Category 0": "Category 0",
    "Category 1": "Category 1",
    "Category 2": "Category 2",
    "Category 3": "Category 3",
    "Category 4": "Category 4",
    "companyUrl": "companyUrl",
    "vkontakte": "vkontakte",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
}

# Ключевые колонки из Webbee AI (TSV/CSV формат)
KEY_COLUMNS_CSV = list(KEY_COLUMNS_JSON.keys())

PHONE_COLUMNS = ("phone_1", "phone_2")
PHONE_CLEAN_COLUMNS = ("phone_1_clean", "phone_2_clean")

# Колонки для экспорта в Битрикс (промежуточный формат)
OUTPUT_COLUMNS = [
    "Название лида",
    "Рабочий телефон",
    "Мобильный телефон",
    "Адрес",
    "Корпоративный сайт",
    "Контакт Telegram",
    "Контакт ВКонтакте",
    "Название компании",
    "Источник телефона",
    "Ответственный",
]
PREVIEW_COLUMNS = [
    "Название лида",
    "Рабочий телефон",
    "Адрес",
    "Ответственный",
    "Источник телефона",
]

DELIMITED_FILE_SEPARATORS = {
    ".tsv": "\t",
    ".csv": ",",
}


def load_file(filepath: str) -> pd.DataFrame | None:
    """
    Загружает TSV, CSV или JSON файл.

    Args:
        filepath: Путь к файлу

    Returns:
        DataFrame или None, если ошибка загрузки
        
    Raises:
        SecurityError: Если путь к файлу небезопасен
    """
    # Проверка пути на безопасность
    if not is_safe_path(filepath):
        logger.error(f"Попытка доступа к запрещённому пути: {filepath}")
        raise SecurityError(f"Небезопасный путь: {filepath}")
    
    # Проверка существования
    if not Path(filepath).exists():
        logger.error(f"Файл не существует: {filepath}")
        return None
    
    # Проверка расширения
    ext = Path(filepath).suffix.lower()
    if ext not in {".json", ".tsv", ".csv"}:
        logger.error(f"Неподдерживаемое расширение: {ext}")
        return None
    
    try:
        ext = Path(filepath).suffix.lower()

        if ext == ".json":
            # Загрузка JSON (массив объектов)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                logger.error(f"Файл {filepath} должен содержать JSON массив")
                return None

        elif ext in DELIMITED_FILE_SEPARATORS:
            df = pd.read_csv(
                filepath,
                sep=DELIMITED_FILE_SEPARATORS[ext],
                encoding="utf-8",
                dtype=str,
                low_memory=False,
            )
        else:
            # Пытаемся определить формат автоматически
            df = pd.read_csv(filepath, encoding="utf-8", dtype=str, low_memory=False)

        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {filepath}: {e}", exc_info=True)
        return None


def clean_phone_column(
    series: pd.Series, phone_format: str = "7", min_length: int = 10
) -> pd.Series:
    """
    Применяет очистку телефона к серии данных.

    Args:
        series: Серия с телефонами
        phone_format: Целевой формат телефона
        min_length: Минимальная длина номера

    Returns:
        Серия с нормализованными телефонами
    """
    from functools import partial

    cleaner = partial(clean_phone, phone_format=phone_format, min_length=min_length)
    return series.apply(cleaner)


def _rename_json_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Переименовывает колонки JSON в наш формат.

    Args:
        df: Исходный DataFrame

    Returns:
        DataFrame с переименованными колонками
    """
    rename_map = {}
    for our_name, json_name in KEY_COLUMNS_JSON.items():
        if json_name in df.columns:
            rename_map[json_name] = our_name

    if rename_map:
        df = df.rename(columns=rename_map)
        logger.debug(f"Переименовано колонок: {len(rename_map)}")

    return df


def _clean_phones(
    df: pd.DataFrame, phone_format: str, min_length: int, ignore_phone_2: bool
) -> pd.DataFrame:
    """
    Очищает телефоны в DataFrame.

    Args:
        df: DataFrame с данными
        phone_format: Формат телефона
        min_length: Минимальная длина
        ignore_phone_2: Игнорировать phone_2

    Returns:
        DataFrame с очищенными телефонами
    """
    if "phone_1" in df.columns:
        df["phone_1_clean"] = clean_phone_column(
            df["phone_1"], phone_format=phone_format, min_length=min_length
        )
    else:
        df["phone_1_clean"] = None

    if "phone_2" in df.columns and not ignore_phone_2:
        df["phone_2_clean"] = clean_phone_column(
            df["phone_2"], phone_format=phone_format, min_length=min_length
        )
    else:
        df["phone_2_clean"] = None

    return df


def _select_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Выбирает нужные колонки для экспорта.

    Args:
        df: DataFrame с данными

    Returns:
        DataFrame с выбранными колонками
    """
    cols_to_keep = [
        col for col in KEY_COLUMNS_CSV if col not in PHONE_COLUMNS and col in df.columns
    ]
    cols_to_keep += [col for col in PHONE_CLEAN_COLUMNS if col in df.columns]
    cols_to_keep.append("Источник телефона")

    return df[[col for col in cols_to_keep if col in df.columns]]


def process_file(
    filepath: str, source_name: str, processing_settings: dict | None = None
) -> pd.DataFrame | None:
    """
    Обрабатывает один файл: загружает, чистит телефоны, фильтрует строки.

    Args:
        filepath: Путь к файлу
        source_name: Имя файла (источник)
        processing_settings: Настройки обработки

    Returns:
        Обработанный DataFrame или None
        
    Raises:
        SecurityError: Если путь к файлу небезопасен
    """
    # Проверка пути на безопасность
    if not is_safe_path(filepath):
        logger.error(f"Небезопасный путь: {filepath}")
        raise SecurityError(f"Небезопасный путь: {filepath}")
    
    processing_settings = processing_settings or {}
    ignore_phone_2 = processing_settings.get("ignore_phone_2", False)
    phone_format = processing_settings.get("phone_format", "7")
    min_phone_length = processing_settings.get("min_phone_length", 10)

    df = load_file(filepath)
    if df is None:
        return None

    ext = Path(filepath).suffix.lower()

    # Для JSON формата переименовываем колонки
    if ext == ".json":
        df = _rename_json_columns(df)

    # Проверяем наличие ключевых колонок
    if "Название" not in df.columns or not any(
        column in df.columns for column in PHONE_COLUMNS
    ):
        logger.error(f"Файл {filepath} не содержит обязательных колонок")
        return None

    # Очищаем телефоны
    df = _clean_phones(df, phone_format, min_phone_length, ignore_phone_2)

    # Удаляем строки, где оба телефона невалидны
    df = df[(df["phone_1_clean"].notna()) | (df["phone_2_clean"].notna())]

    # Добавляем источник телефона
    df["Источник телефона"] = source_name

    # Выбираем только нужные колонки
    df = _select_output_columns(df)

    # Переименовываем очищенные телефоны
    df = df.rename(columns={"phone_1_clean": "phone_1", "phone_2_clean": "phone_2"})

    return df


def _combine_phone_columns(df: pd.DataFrame) -> pd.Series:
    """
    Объединяет phone_1 и phone_2 в одну строку для поиска дубликатов.

    Args:
        df: DataFrame с данными

    Returns:
        Series с объединёнными телефонами
    """
    phone_1 = df.get("phone_1")
    if phone_1 is None:
        phone_1 = pd.Series("", index=df.index)
    else:
        phone_1 = phone_1.fillna("").astype(str)

    phone_2 = df.get("phone_2")
    if phone_2 is None:
        phone_2 = pd.Series("", index=df.index)
    else:
        phone_2 = phone_2.fillna("").astype(str)

    return phone_1 + "|" + phone_2


def remove_duplicates(
    df: pd.DataFrame, remove_duplicates_flag: bool = True
) -> tuple[pd.DataFrame, int]:
    """
    Удаляет дубликаты по номерам телефонов.

    Args:
        df: DataFrame с данными
        remove_duplicates_flag: Флаг удаления дубликатов

    Returns:
        Кортеж (DataFrame без дубликатов, количество удалённых дубликатов)
    """
    if not remove_duplicates_flag:
        return df, 0

    initial_count = len(df)

    phones_combined = _combine_phone_columns(df)
    duplicates_mask = phones_combined.duplicated()
    duplicates_count = int(duplicates_mask.sum())
    logger.info(f"Найдено дубликатов: {duplicates_count}")

    # Логируем топ дублирующихся телефонов
    if duplicates_count > 0:
        phone_counts = phones_combined.value_counts()
        top_duplicates = phone_counts[phone_counts > 1].head(10)
        for phone, count in top_duplicates.items():
            logger.info(f"Дубликат телефона {phone}: {count} раз")

    # Удаляем дубликаты, оставляя первое вхождение
    df = df.loc[~duplicates_mask].copy()

    duplicates_removed = initial_count - len(df)

    logger.info(f"Удалено дубликатов: {duplicates_removed}, осталось лидов: {len(df)}")

    return df, duplicates_removed


def assign_managers(df: pd.DataFrame, managers: list[str]) -> pd.DataFrame:
    """
    Распределяет лиды по менеджерам по круговому алгоритму (round-robin).

    Args:
        df: DataFrame с лидами
        managers: Список имён менеджеров

    Returns:
        DataFrame с добавленной колонкой 'Ответственный'
    """
    # Обработка пустого DataFrame
    if df.empty:
        df["Ответственный"] = ""
        return df

    if not managers:
        df["Ответственный"] = "Не назначен"
        return df

    df = df.copy()
    df["Ответственный"] = [managers[i % len(managers)] for i in range(len(df))]

    return df


def merge_files(
    filepaths: list[str], managers: list[str], processing_settings: dict | None = None
) -> tuple[pd.DataFrame, dict]:
    """
    Обрабатывает и объединяет несколько файлов.

    Args:
        filepaths: Список путей к файлам
        managers: Список менеджеров для распределения
        processing_settings: Настройки обработки (phone_format, remove_duplicates, etc.)

    Returns:
        Кортеж (объединённый DataFrame, статистика обработки)
    """
    processing_settings = processing_settings or {}

    all_data = []
    stats = {
        "files_processed": 0,
        "total_rows": 0,
        "duplicates_removed": 0,
        "rows_without_phones": 0,
    }

    # Обрабатываем каждый файл
    for filepath in filepaths:
        source_name = os.path.basename(filepath)
        df = process_file(filepath, source_name, processing_settings)

        if df is not None:
            initial_rows = len(df)
            all_data.append(df)
            stats["files_processed"] += 1
            stats["total_rows"] += initial_rows

            logger.info(f"Обработан файл {source_name}: {initial_rows} строк")

    if not all_data:
        logger.warning("Ни один файл не был обработан")
        return pd.DataFrame(), stats

    # Объединяем все данные (один concat вместо нескольких)
    logger.info(f"Объединение {len(all_data)} файлов...")
    merged = pd.concat(all_data, ignore_index=True)

    # Освобождаем память
    del all_data

    # Удаляем дубликаты (с учётом настройки)
    remove_duplicates_flag = processing_settings.get("remove_duplicates", True)
    merged, duplicates_removed = remove_duplicates(merged, remove_duplicates_flag)
    stats["duplicates_removed"] = duplicates_removed

    logger.info(f"Удалено дубликатов: {duplicates_removed}")

    # Распределяем по менеджерам
    merged = assign_managers(merged, managers)

    # Формируем итоговые колонки
    merged = prepare_output_columns(merged)

    logger.info(f"Итого лидов: {len(merged)}")

    return merged, stats


def prepare_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготавливает итоговые колонки для экспорта.

    Args:
        df: DataFrame с обработанными данными

    Returns:
        DataFrame с колонками для экспорта
    """
    result = pd.DataFrame()

    # Название лида = [Category 0] - [Название] (векторизованная версия)
    if "Category 0" in df.columns and "Название" in df.columns:
        category = df["Category 0"].fillna("")
        name = df["Название"].fillna("")
        mask = (category != "") & (name != "")

        result["Название лида"] = name.copy()
        result.loc[mask, "Название лида"] = category[mask] + " - " + name[mask]
    else:
        result["Название лида"] = df.get("Название", "")

    # Телефоны
    result["Рабочий телефон"] = df.get("phone_1", "")
    result["Мобильный телефон"] = df.get("phone_2", "")

    # Адрес
    result["Адрес"] = df.get("Адрес", "")

    # Сайт (без UTM-меток)
    result["Корпоративный сайт"] = df.get("companyUrl", "")

    # Соцсети
    result["Контакт Telegram"] = df.get("telegram", "")
    result["Контакт ВКонтакте"] = df.get("vkontakte", "")

    # Название компании
    result["Название компании"] = df.get("Название", "")

    # Источник и ответственный
    result["Источник телефона"] = df.get("Источник телефона", "")
    result["Ответственный"] = df.get("Ответственный", "Не назначен")

    return result.reindex(columns=OUTPUT_COLUMNS)


def get_preview_data(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Возвращает данные для предпросмотра.

    Args:
        df: DataFrame с данными
        limit: Количество строк для предпросмотра

    Returns:
        DataFrame с первыми N строками
    """
    available_cols = [col for col in PREVIEW_COLUMNS if col in df.columns]

    return df[available_cols].head(limit)
