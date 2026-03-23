"""
Генератор ссылок для Яндекс.Карт.

Генерация поисковых ссылок по запросам вида [Сегмент] + [Регион].
"""

import copy
import csv

_DEFAULT_CITY_SLUGS = {
    "Москва": "moscow",
    "Санкт-Петербург": "saint-petersburg",
    "Екатеринбург": "yekaterinburg",
    "Новосибирск": "novosibirsk",
    "Казань": "kazan",
    "Нижний Новгород": "nizhny-novgorod",
    "Челябинск": "chelyabinsk",
    "Самара": "samara",
    "Омск": "omsk",
    "Ростов-на-Дону": "rostov-na-donu",
    "Уфа": "ufa",
    "Красноярск": "krasnoyarsk",
    "Пермь": "perm",
    "Воронеж": "voronezh",
    "Волгоград": "volgograd",
    "Краснодар": "krasnodar",
    "Саратов": "saratov",
    "Тюмень": "tyumen",
    "Тольятти": "tolyatti",
    "Ижевск": "izhevsk",
    "Барнаул": "barnaul",
    "Ульяновск": "ulyanovsk",
    "Иркутск": "irkutsk",
    "Хабаровск": "khabarovsk",
    "Ярославль": "yaroslavl",
    "Владивосток": "vladivostok",
    "Махачкала": "makhachkala",
    "Томск": "tomsk",
    "Оренбург": "orenburg",
    "Кемерово": "kemerovo",
    "Новокузнецк": "novokuznetsk",
    "Рязань": "ryazan",
    "Астрахань": "astrakhan",
    "Пенза": "penza",
    "Липецк": "lipetsk",
    "Киров": "kirov",
    "Чебоксары": "cheboksary",
    "Тула": "tula",
    "Калининград": "kaliningrad",
    "Балашиха": "balashikha",
    "Курск": "kursk",
    "Севастополь": "sevastopol",
    "Сочи": "sochi",
}

_DEFAULT_REGIONS = [
    # Мегаполисы с районами
    "Москва",
    "Санкт-Петербург",
    # Города-миллионники
    "Екатеринбург",
    "Новосибирск",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
    "Уфа",
    "Красноярск",
    "Пермь",
    "Воронеж",
    "Волгоград",
    "Краснодар",
    "Саратов",
    "Тюмень",
    "Тольятти",
    "Ижевск",
    "Барнаул",
    "Ульяновск",
    "Иркутск",
    "Хабаровск",
    "Ярославль",
    "Владивосток",
    "Махачкала",
    "Томск",
    "Оренбург",
    "Кемерово",
    "Новокузнецк",
    "Рязань",
    "Астрахань",
    "Пенза",
    "Липецк",
    "Киров",
    "Чебоксары",
    "Тула",
    "Калининград",
    "Балашиха",
    "Курск",
    "Севастополь",
    "Сочи",
]

_DEFAULT_CITY_DISTRICTS = {
    # Районы Москвы
    "Москва": [
        "ЦАО",
        "САО",
        "СВАО",
        "ВАО",
        "ЮВАО",
        "ЮАО",
        "ЮЗАО",
        "ЗАО",
        "СЗАО",
        "Зеленоград",
        "Троицкий АО",
        "Новомосковский АО",
    ],
    # Районы Санкт-Петербурга
    "Санкт-Петербург": [
        "Адмиралтейский",
        "Василеостровский",
        "Выборгский",
        "Калининский",
        "Кировский",
        "Колпинский",
        "Красногвардейский",
        "Красносельский",
        "Кронштадтский",
        "Курортный",
        "Московский",
        "Невский",
        "Петроградский",
        "Петродворцовый",
        "Приморский",
        "Пушкинский",
        "Фрунзенский",
        "Центральный",
    ],
}


def generate_yandex_maps_link(segment: str, region: str) -> str:
    """
    Генерирует ссылку для Яндекс.Карт.

    Args:
        segment: Поисковый запрос (например, "Металлоконструкции")
        region: Регион (например, "Москва")

    Returns:
        Ссылка на Яндекс.Карты в формате yandex.ru/maps/213/moscow/search/...
    """
    # Кодируем пробелы как %20 вместо +
    query = f"{segment} {region}"
    encoded_query = query.replace(" ", "%20")

    # Формируем URL в формате Яндекс.Карт
    return f"https://yandex.ru/maps/213/moscow/search/{encoded_query}"


def get_city_slug(region: str) -> str:
    """
    Возвращает slug города для Яндекс.Карт.

    Args:
        region: Название региона

    Returns:
        Slug города (например, "moscow" для "Москва")
    """
    # Проверяем точное совпадение
    if region in _DEFAULT_CITY_SLUGS:
        return _DEFAULT_CITY_SLUGS[region]

    # Проверяем часть региона (если указан район)
    for city in _DEFAULT_CITY_SLUGS.keys():
        if region.startswith(city):
            return _DEFAULT_CITY_SLUGS[city]

    # По умолчанию используем moscow
    return "moscow"


def generate_links(segment: str, regions: list[str]) -> list[str]:
    """
    Генерирует список ссылок для всех регионов.

    Args:
        segment: Поисковый запрос
        regions: Список регионов

    Returns:
        Список ссылок
    """
    return [generate_yandex_maps_link(segment, region) for region in regions]


def generate_links_batch(segments: list[str], regions: list[str]) -> list[dict]:
    """
    Пакетная генерация ссылок для всех сегментов и регионов.

    Args:
        segments: Список поисковых запросов
        regions: Список регионов

    Returns:
        Список словарей {segment, region, link}
    """
    return [
        {
            "segment": segment,
            "region": region,
            "link": generate_yandex_maps_link(segment, region),
        }
        for segment in segments
        for region in regions
    ]


def save_links_to_csv(links: list[dict], filepath: str) -> bool:
    """
    Сохраняет ссылки в CSV файл.

    Args:
        links: Список ссылок (словари)
        filepath: Путь к файлу

    Returns:
        True если успешно
    """
    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["segment", "region", "link"], delimiter=";"
            )
            writer.writeheader()
            writer.writerows(links)

        return True
    except Exception as e:
        print(f"Ошибка сохранения CSV: {e}")
        return False


def load_regions_from_config(config: dict) -> list[str]:
    """
    Загружает список регионов из конфигурации.

    Args:
        config: Словарь конфигурации

    Returns:
        Список регионов
    """
    regions = config.get("regions", None)

    # Если регионов нет в конфиге, возвращаем базовый список
    if not regions:
        return list(_DEFAULT_REGIONS)

    return regions


def add_region(config: dict, region: str) -> dict:
    """
    Добавляет регион в список.

    Args:
        config: Словарь конфигурации
        region: Регион для добавления

    Returns:
        Обновлённая конфигурация
    """
    regions = config.get("regions", [])
    if region not in regions:
        regions.append(region)
        config["regions"] = regions
    return config


def remove_region(config: dict, region: str) -> dict:
    """
    Удаляет регион из списка.

    Args:
        config: Словарь конфигурации
        region: Регион для удаления

    Returns:
        Обновлённая конфигурация
    """
    regions = config.get("regions", [])
    if region in regions:
        regions.remove(region)
        config["regions"] = regions
    return config


def load_city_districts(config: dict) -> dict:
    """
    Загружает районы городов из конфигурации.

    Args:
        config: Словарь конфигурации

    Returns:
        Словарь {город: [районы]}
    """
    city_districts = config.get("city_districts", None)

    # Если районов нет в конфиге, возвращаем базовый список
    if not city_districts:
        return copy.deepcopy(_DEFAULT_CITY_DISTRICTS)

    return city_districts
