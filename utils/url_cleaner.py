"""
Модуль очистки URL от UTM-меток и лишних параметров.
"""

import logging
from urllib.parse import ParseResult, parse_qs, urlencode, urlparse

# Настраиваем логгер
logger = logging.getLogger("url_cleaner")

# Константы
UTM_PREFIXES = ("utm_", "yclid", "gclid", "fbclid", "_openstat", "_ga", "_gl")
DEFAULT_URL_TIMEOUT = 5  # секунд
_INVALID_URL_VALUES = {"none", "nan", ""}


def _is_empty_url(url: str | None) -> bool:
    if url is None:
        return True
    if not isinstance(url, str):
        return False
    if not url:
        return True
    return url.lower() in _INVALID_URL_VALUES


def _parse_with_optional_scheme(url: str) -> tuple[str, ParseResult]:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
        parsed = urlparse(url)
    return url, parsed


def clean_url(url: str | None, keep_params: tuple[str, ...] | None = None) -> str:
    """
    Очищает URL от UTM-меток и лишних параметров.

    Args:
        url: Исходный URL
        keep_params: Дополнительные параметры для сохранения (кортеж)

    Returns:
        Очищенный URL или пустая строка

    Example:
        >>> clean_url('https://example.com?utm_source=google&utm_medium=cpc')
        'https://example.com'
    """
    if _is_empty_url(url):
        return ""

    url = url.strip()

    try:
        url, parsed = _parse_with_optional_scheme(url)

        # Если URL невалидный
        if not parsed.netloc:
            logger.debug(f"Невалидный URL: {url}")
            return url

        # Парсим параметры
        params = parse_qs(parsed.query)

        # Параметры, которые стоит сохранить (не UTM)
        keep_params_set = set(keep_params) if keep_params else set()
        cleaned_params = {}

        for key, value in params.items():
            key_lower = key.lower()
            # Пропускаем UTM-метки и служебные параметры метрик
            if key_lower.startswith("utm_") or key_lower in UTM_PREFIXES:
                continue
            # Сохраняем остальные параметры
            if value and value[0]:
                cleaned_params[key] = value[0]
            elif key in keep_params_set:
                cleaned_params[key] = value[0] if value else ""

        # Формируем новый URL
        new_query = urlencode(cleaned_params) if cleaned_params else ""

        # Собираем URL
        cleaned = parsed.scheme + "://" + parsed.netloc + parsed.path
        if new_query:
            cleaned += "?" + new_query

        logger.debug(f"URL очищён: {url} -> {cleaned}")
        return cleaned

    except Exception as e:
        logger.error(f"Ошибка очистки URL {url}: {e}", exc_info=True)
        # Если ошибка парсинга, возвращаем исходный URL
        return url


def extract_domain(url: str | None) -> str:
    """
    Извлекает домен из URL.

    Args:
        url: URL

    Returns:
        Доменное имя или пустая строка

    Example:
        >>> extract_domain('https://example.com/path')
        'example.com'
    """
    if _is_empty_url(url):
        return ""

    try:
        raw_url = url
        _, parsed = _parse_with_optional_scheme(url)

        if not parsed.netloc:
            logger.debug(f"Не удалось извлечь домен: {raw_url}")
            return raw_url

        return parsed.netloc

    except Exception as e:
        logger.error(f"Ошибка извлечения домена {url}: {e}", exc_info=True)
        return url or ""


def normalize_social_url(url: str | None, platform: str = "vk") -> str:
    """
    Нормализует URL социальной сети (удаляет лишнее, оставляет username).

    Args:
        url: URL или username
        platform: Платформа ('vk', 'telegram')

    Returns:
        Username или пустая строка

    Example:
        >>> normalize_social_url('https://t.me/username', 'telegram')
        'username'
    """
    if _is_empty_url(url):
        return ""

    url = url.strip()

    # Если это уже не URL, а просто username
    if "/" not in url and "." not in url:
        return url.lstrip("@")

    try:
        platform_lower = platform.lower()

        if platform_lower == "telegram":
            # Telegram: https://t.me/username -> username
            if "t.me" in url:
                parts = url.split("t.me/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].lstrip("@")
                    logger.debug(f"Telegram username: {username}")
                    return username

        elif platform_lower == "vk":
            # ВКонтакте: https://vk.com/username -> username
            if "vk.com" in url:
                parts = url.split("vk.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].lstrip("@")
                    logger.debug(f"VK username: {username}")
                    return username
        else:
            logger.warning(f"Неизвестная платформа: {platform}")

        return url

    except Exception as e:
        logger.error(f"Ошибка нормализации social URL {url}: {e}", exc_info=True)
        return url


def is_valid_url(url: str | None) -> bool:
    """
    Проверяет валидность URL.

    Args:
        url: URL для проверки

    Returns:
        True, если URL валидный

    Example:
        >>> is_valid_url('https://example.com')
        True
        >>> is_valid_url('not-a-url')
        False
    """
    if not url or not isinstance(url, str):
        return False

    try:
        _, parsed = _parse_with_optional_scheme(url)

        # Проверяем наличие домена
        return bool(parsed.netloc)

    except Exception:
        return False
