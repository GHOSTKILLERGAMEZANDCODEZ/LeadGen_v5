"""
Модуль валидации и нормализации телефонных номеров.

Правила:
- Поддержка форматов: 7XXXXXXXXXX, 8XXXXXXXXXX, +7XXXXXXXXXX
- Удаляются все нецифровые символы
- Конвертируется из научной нотации (если есть)
- Битые номера (короче мин. длины, не начинаются с 7/8) — невалидные
"""

import re

# Константы
DEFAULT_PHONE_FORMAT = "7"
DEFAULT_MIN_LENGTH = 10
RUSSIA_MOBILE_PREFIX = "9"
RUSSIA_PREFIX = "7"
ALTERNATIVE_PREFIX = "8"
NAN_LIKE_VALUES = {"nan", "none", "", "null"}
NON_DIGIT_RE = re.compile(r"\D")
VALID_PHONE_RE = re.compile(r"^[78]\d{10}$")


def clean_phone(
    phone: str | float | int | None,
    phone_format: str = DEFAULT_PHONE_FORMAT,
    min_length: int = DEFAULT_MIN_LENGTH,
) -> str | None:
    """
    Очищает и нормализует телефонный номер.

    Args:
        phone: Исходное значение (строка, число, float из pandas)
        phone_format: Целевой формат ('7', '8', '+7')
        min_length: Минимальная длина номера

    Returns:
        Нормализованный номер или None, если номер невалидный
    """
    if phone is None:
        return None

    # Конвертируем в строку
    phone_str = str(phone)

    # Проверяем на NaN/пустые значения
    if phone_str.lower() in NAN_LIKE_VALUES:
        return None

    # Если число в научной нотации (например, 7.8005001695e+10)
    try:
        # Пытаемся конвертировать в float и затем в int
        phone_float = float(phone_str)
        if phone_float != 0:
            phone_str = str(int(phone_float))
    except (ValueError, OverflowError):
        pass

    # Удаляем все нецифровые символы
    digits = NON_DIGIT_RE.sub("", phone_str)

    # Проверяем длину
    if len(digits) < min_length:
        return None

    # Если номер начинается с 9 (мобильные РФ) или 8 — добавляем/заменяем префикс
    if digits.startswith(RUSSIA_MOBILE_PREFIX) and len(digits) == 10:
        digits = RUSSIA_PREFIX + digits
    elif digits.startswith(ALTERNATIVE_PREFIX) and len(digits) == 11:
        digits = RUSSIA_PREFIX + digits[1:]

    # Проверяем, что номер начинается с 7 и имеет 10-11 цифр
    if not digits.startswith(RUSSIA_PREFIX):
        return None

    if len(digits) < 10 or len(digits) > 11:
        return None

    # Форматируем согласно настройкам
    return format_phone(digits, phone_format)


def format_phone(phone: str, phone_format: str = DEFAULT_PHONE_FORMAT) -> str:
    """
    Форматирует номер телефона согласно выбранному формату.

    Args:
        phone: Номер (начинается с 7, без +)
        phone_format: Целевой формат ('7', '8', '+7')

    Returns:
        Отформатированный номер
    """
    # Удаляем первую цифру (7) для форматирования
    if phone.startswith(RUSSIA_PREFIX):
        base = phone[1:]
    else:
        base = phone

    if phone_format == ALTERNATIVE_PREFIX:
        return ALTERNATIVE_PREFIX + base
    elif phone_format == "+" + RUSSIA_PREFIX:
        return "+" + RUSSIA_PREFIX + base
    else:  # phone_format == '7'
        return RUSSIA_PREFIX + base


def validate_phone(phone: str | None, min_length: int = DEFAULT_MIN_LENGTH) -> bool:
    """
    Проверяет валидность телефона.

    Args:
        phone: Нормализованный номер
        min_length: Минимальная длина

    Returns:
        True, если номер валидный
    """
    if phone is None:
        return False

    # Очищаем от форматирования для проверки
    digits = NON_DIGIT_RE.sub("", phone)

    if len(digits) < min_length:
        return False

    return bool(VALID_PHONE_RE.match(digits))


def extract_phone_from_any(
    value: str | float | int | None,
    phone_format: str = DEFAULT_PHONE_FORMAT,
    min_length: int = DEFAULT_MIN_LENGTH,
) -> str | None:
    """
    Извлекает телефон из любого формата данных.

    Это обёртка над clean_phone для обратной совместимости.

    Args:
        value: Исходное значение любого типа
        phone_format: Целевой формат
        min_length: Минимальная длина

    Returns:
        Нормализованный номер или None
    """
    return clean_phone(value, phone_format, min_length)
