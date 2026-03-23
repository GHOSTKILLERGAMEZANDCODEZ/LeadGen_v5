"""
Часовые пояса городов России.

Модуль предоставляет словарь городов России с их часовыми поясами
и функцию для получения часового пояса города.

Example:
    >>> from utils.city_timezones import get_city_timezone
    >>> get_city_timezone("Москва")
    'UTC+3'
    >>> get_city_timezone("Владивосток")
    'UTC+10'
"""

# Часовые пояса городов России (UTC+offset)
# Источник: https://ru.wikipedia.org/wiki/Часовые_пояса_России
CITY_TIMEZONES: dict[str, str] = {
    # UTC+2 (Калининградское время)
    "Калининград": "UTC+2",
    
    # UTC+3 (Московское время)
    "Москва": "UTC+3",
    "Санкт-Петербург": "UTC+3",
    "Екатеринбург": "UTC+3",
    "Новосибирск": "UTC+3",
    "Казань": "UTC+3",
    "Нижний Новгород": "UTC+3",
    "Челябинск": "UTC+3",
    "Самара": "UTC+3",
    "Омск": "UTC+3",
    "Ростов-на-Дону": "UTC+3",
    "Уфа": "UTC+3",
    "Красноярск": "UTC+3",
    "Пермь": "UTC+3",
    "Воронеж": "UTC+3",
    "Волгоград": "UTC+3",
    "Краснодар": "UTC+3",
    "Саратов": "UTC+3",
    "Тюмень": "UTC+3",
    "Тольятти": "UTC+3",
    "Ижевск": "UTC+3",
    "Барнаул": "UTC+3",
    "Ульяновск": "UTC+3",
    "Иркутск": "UTC+3",
    "Ярославль": "UTC+3",
    "Махачкала": "UTC+3",
    "Томск": "UTC+3",
    "Оренбург": "UTC+3",
    "Кемерово": "UTC+3",
    "Новокузнецк": "UTC+3",
    "Рязань": "UTC+3",
    "Астрахань": "UTC+3",
    "Пенза": "UTC+3",
    "Липецк": "UTC+3",
    "Киров": "UTC+3",
    "Чебоксары": "UTC+3",
    "Тула": "UTC+3",
    "Балашиха": "UTC+3",
    "Курск": "UTC+3",
    "Севастополь": "UTC+3",
    "Сочи": "UTC+3",
    
    # UTC+4 (Самарское время)
    "Самара": "UTC+4",  # Самара фактически в UTC+4
    "Ижевск": "UTC+4",  # Ижевск в UTC+4
    "Ульяновск": "UTC+4",  # Ульяновск в UTC+4
    "Саратов": "UTC+4",  # Саратов в UTC+4
    "Астрахань": "UTC+4",  # Астрахань в UTC+4
    
    # UTC+5 (Екатеринбургское время)
    "Екатеринбург": "UTC+5",
    "Пермь": "UTC+5",
    "Челябинск": "UTC+5",
    "Оренбург": "UTC+5",
    "Уфа": "UTC+5",
    "Курган": "UTC+5",
    
    # UTC+6 (Омское время)
    "Омск": "UTC+6",
    
    # UTC+7 (Красноярское время)
    "Красноярск": "UTC+7",
    "Новосибирск": "UTC+7",
    "Кемерово": "UTC+7",
    "Новокузнецк": "UTC+7",
    "Томск": "UTC+7",
    
    # UTC+8 (Иркутское время)
    "Иркутск": "UTC+8",
    
    # UTC+9 (Якутское время)
    "Якутск": "UTC+9",
    "Чита": "UTC+9",
    "Благовещенск": "UTC+9",
    
    # UTC+10 (Владивостокское время)
    "Владивосток": "UTC+10",
    "Хабаровск": "UTC+10",
    "Комсомольск-на-Амуре": "UTC+10",
    "Уссурийск": "UTC+10",
    "Находка": "UTC+10",
    
    # UTC+11 (Среднеколымское время)
    "Магадан": "UTC+11",
    "Южно-Сахалинск": "UTC+11",
    "Сахалин": "UTC+11",
    
    # UTC+12 (Камчатское время)
    "Петропавловск-Камчатский": "UTC+12",
    "Камчатка": "UTC+12",
}


def get_city_timezone(city: str) -> str | None:
    """
    Возвращает часовой пояс города.

    Args:
        city: Название города (например, "Москва", "Владивосток")

    Returns:
        Часовой пояс в формате "UTC+X" или None если город не найден.

    Example:
        >>> get_city_timezone("Москва")
        'UTC+3'
        >>> get_city_timezone("Владивосток")
        'UTC+10'
        >>> get_city_timezone("Неизвестный")
        None
    """
    # Точное совпадение
    if city in CITY_TIMEZONES:
        return CITY_TIMEZONES[city]
    
    # Проверка частичного совпадения (для городов с районами)
    for city_name in CITY_TIMEZONES.keys():
        if city.startswith(city_name):
            return CITY_TIMEZONES[city_name]
    
    # Город не найден
    return None


def get_city_timezone_with_name(city: str) -> str | None:
    """
    Возвращает часовой пояс города с названием.

    Args:
        city: Название города

    Returns:
        Строка в формате "Город - UTC+X" или None если город не найден.

    Example:
        >>> get_city_timezone_with_name("Москва")
        'Москва - UTC+3'
        >>> get_city_timezone_with_name("Владивосток")
        'Владивосток - UTC+10'
    """
    timezone = get_city_timezone(city)
    if timezone:
        return f"{city} - {timezone}"
    return None


def format_city_with_timezone(city: str, show_timezone: bool = True) -> str:
    """
    Форматирует название города с часовым поясом.

    Args:
        city: Название города
        show_timezone: Показывать ли часовой пояс

    Returns:
        Строка в формате "Город (UTC+X)" или просто "Город".

    Example:
        >>> format_city_with_timezone("Москва")
        'Москва (UTC+3)'
        >>> format_city_with_timezone("Москва", show_timezone=False)
        'Москва'
    """
    if not show_timezone:
        return city

    timezone = get_city_timezone(city)
    if timezone:
        return f"{city} ({timezone})"
    return city


def add_custom_timezone(city: str, timezone: str) -> None:
    """
    Добавляет пользовательский часовой пояс для города.
    
    Args:
        city: Название города
        timezone: Часовой пояс в формате "UTC+X"
    
    Example:
        >>> add_custom_timezone("Владивосток", "UTC+10")
    """
    if city and timezone:
        CITY_TIMEZONES[city] = timezone
