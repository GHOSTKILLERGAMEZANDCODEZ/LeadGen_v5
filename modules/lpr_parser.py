"""
Парсер сайтов для поиска ЛПР (Лиц Принимающих Решения).

Поиск ФИО, должностей и ИНН на сайтах компаний.
"""

import re
import csv
import socket
import ipaddress
from typing import Dict
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Паттерны для поиска
PATTERNS = {
    "director": [
        r"генеральный\s+директор",
        r"директор",
        r"руководитель",
        r"исполнительный\s+директор",
        r"коммерческий\s+директор",
        r"финансовый\s+директор",
        r"управляющий",
        r"президент",
        r"председатель",
    ],
    "fio": [
        r"([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)",  # Полное ФИО
        r"([А-ЯЁ][а-яё]+)\s+([А-ЯЁ]\.)\s+([А-ЯЁ]\.)",  # Фамилия И.О.
    ],
    "inn": [
        r"ИНН\s*(\d{10}|\d{12})",
        r"ИНН/КПП\s*(\d{10}|\d{12})",
    ],
    "phone": [
        r"(\+7|8)\s*\(?[0-9]{3}\)?\s*[0-9]{3}\s*[0-9]{2}\s*[0-9]{2}",
    ],
    "email": [
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    ],
}

# Страницы для поиска
TARGET_PAGES = [
    "",  # Главная
    "/contacts",
    "/contact",
    "/contacts.html",
    "/team",
    "/about",
    "/about-us",
    "/leadership",
    "/management",
    "/rukovodstvo",
    "/kontakty",
]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DEFAULT_TIMEOUT = 10


def is_safe_url(url: str) -> bool:
    """
    Проверяет безопасность URL перед запросом (SSRF защита).
    
    Защита от SSRF атак:
    - Только HTTPS схемы
    - Блокировка частных IP адресов
    - Блокировка localhost и внутренних доменов

    Args:
        url: URL для проверки

    Returns:
        True если URL безопасен, False иначе
    """
    try:
        parsed = urlparse(url)
        
        # Только HTTPS
        if parsed.scheme != "https":
            return False
        
        # Проверяем hostname
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Блокируем localhost и внутренние домены
        blocked_domains = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
        if hostname.lower() in blocked_domains:
            return False
        
        # Блокируем внутренние домены
        if hostname.endswith('.local') or hostname.endswith('.internal'):
            return False
        
        # Проверяем IP адрес на частные диапазоны
        try:
            ip = socket.gethostbyname(hostname)
            ip_addr = ipaddress.ip_address(ip)
            if ip_addr.is_private or ip_addr.is_loopback or ip_addr.is_link_local:
                return False
        except socket.gaierror:
            # Не удалось разрешить hostname
            return False
        
        return True
    except Exception:
        return False


def _empty_result(url: str) -> Dict:
    return {
        "url": url,
        "fio": "",
        "position": "",
        "inn": "",
        "phones": "",
        "emails": "",
    }


def _normalize_base_url(base_url: str) -> str:
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    return base_url.rstrip("/")


def _join_values(values: list[str]) -> str:
    return "; ".join(values) if values else ""


def extract_fio(text: str) -> list[str]:
    """
    Извлекает ФИО из текста.

    Args:
        text: Текст для анализа

    Returns:
        Список найденных ФИО
    """
    fios = []

    # Полное ФИО (Иванов Иван Иванович)
    for match in re.finditer(PATTERNS["fio"][0], text):
        fio = match.group(0)
        if fio not in fios:
            fios.append(fio)

    # Фамилия И.О.
    for match in re.finditer(PATTERNS["fio"][1], text):
        fio = match.group(0)
        if fio not in fios:
            fios.append(fio)

    return fios[:5]  # Ограничиваем количество


def extract_position(text: str) -> str | None:
    """
    Извлекает должность из текста.

    Args:
        text: Текст для анализа

    Returns:
        Должность или None
    """
    for pattern in PATTERNS["director"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Возвращаем контекст вокруг должности
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 30)
            context = text[start:end].strip()
            return context

    return None


def extract_inn(text: str) -> str | None:
    """
    Извлекает ИНН из текста.

    Args:
        text: Текст для анализа

    Returns:
        ИНН или None
    """
    for pattern in PATTERNS["inn"]:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None


def extract_phones(text: str) -> list[str]:
    """
    Извлекает телефоны из текста.

    Args:
        text: Текст для анализа

    Returns:
        Список телефонов
    """
    phones = []
    for pattern in PATTERNS["phone"]:
        for match in re.finditer(pattern, text):
            phone = match.group(0).replace(" ", "").replace("(", "").replace(")", "")
            if phone not in phones:
                phones.append(phone)

    return phones[:5]


def extract_emails(text: str) -> list[str]:
    """
    Извлекает email из текста.

    Args:
        text: Текст для анализа

    Returns:
        Список email
    """
    emails = []
    for pattern in PATTERNS["email"]:
        for match in re.finditer(pattern, text):
            email = match.group(0).lower()
            if email not in emails:
                emails.append(email)

    return emails[:5]


def fetch_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> str | None:
    """
    Загружает HTML страницы с SSRF защитой.

    Args:
        url: URL страницы
        timeout: Таймаут запроса

    Returns:
        HTML контент или None
        
    Security:
        Проверяет URL через is_safe_url() перед запросом
    """
    if not HAS_REQUESTS:
        return None
    
    # SSRF проверка перед запросом
    if not is_safe_url(url):
        logger = logging.getLogger(__name__)
        logger.warning(f"Блокирован небезопасный URL: {url}")
        return None

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None


def parse_html_content(html: str, url: str = "") -> Dict:
    """
    Парсит HTML контент и извлекает информацию о ЛПР.

    Args:
        html: HTML контент
        url: URL страницы (для отладки)

    Returns:
        Словарь с найденной информацией
    """
    if not HAS_REQUESTS:
        return _empty_result(url)

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Удаляем скрипты и стили
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Получаем текст
        text = soup.get_text(separator=" ", strip=True)

        # Извлекаем данные
        fios = extract_fio(text)
        position = extract_position(text)
        inn = extract_inn(text)
        phones = extract_phones(text)
        emails = extract_emails(text)

        return {
            "url": url,
            "fio": _join_values(fios),
            "position": position if position else "",
            "inn": inn if inn else "",
            "phones": _join_values(phones),
            "emails": _join_values(emails),
        }
    except Exception as e:
        return _empty_result(url)


def search_lpr_on_website(base_url: str) -> Dict:
    """
    Ищет ЛПР на сайте компании.

    Args:
        base_url: Базовый URL сайта

    Returns:
        Словарь с найденной информацией
    """
    if not HAS_REQUESTS:
        return _empty_result(base_url)

    # Пробуем главную страницу и целевые страницы
    base_url = _normalize_base_url(base_url)
    pages_to_try = [base_url] + [base_url + page for page in TARGET_PAGES if page]

    for url in pages_to_try:
        html = fetch_url(url)
        if html:
            result = parse_html_content(html, url)
            # Если что-то нашли, возвращаем
            if any([result["fio"], result["position"], result["inn"]]):
                return result

    # Ничего не нашли
    return _empty_result(base_url)


def save_lpr_to_csv(lpr_data: list[dict], filepath: str) -> bool:
    """
    Сохраняет данные ЛПР в CSV файл.

    Args:
        lpr_data: Список словарей с данными ЛПР
        filepath: Путь к файлу

    Returns:
        True если успешно
    """
    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            fieldnames = [
                "company_name",
                "url",
                "fio",
                "position",
                "inn",
                "phones",
                "emails",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(lpr_data)

        return True
    except Exception as e:
        print(f"Ошибка сохранения CSV: {e}")
        return False


def load_companies_from_csv(filepath: str) -> list[dict]:
    """
    Загружает список компаний из CSV.

    Args:
        filepath: Путь к файлу

    Returns:
        Список словарей с компаниями
    """
    companies = []

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                companies.append(
                    {
                        "name": row.get(
                            "Название компании", row.get("Название лида", "")
                        ),
                        "url": row.get("Корпоративный сайт", row.get("companyUrl", "")),
                    }
                )
    except Exception as e:
        print(f"Ошибка загрузки CSV: {e}")

    return companies
