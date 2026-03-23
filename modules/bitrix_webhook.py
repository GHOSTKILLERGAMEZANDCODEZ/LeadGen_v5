"""
Модуль интеграции с Битрикс24 через вебхук.

Позволяет получать данные о лидах и менеджерах в реальном времени
через REST API Битрикс24.

Для работы необходимы права вебхука: crm, user
"""

import requests
import logging
import time
import threading
import re
from datetime import datetime, timedelta
from collections import deque
from collections.abc import Iterable
from requests.adapters import HTTPAdapter, Retry

# Импортируем функцию для чтения переменных окружения
from utils.config_loader import get_env_var

# Импортируем специализированные исключения
from .exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookConnectionError,
    BitrixWebhookError,
)

# Настраиваем логгер
logger = logging.getLogger("bitrix_webhook")

DEFAULT_TIMEOUT = 30
DEFAULT_BATCH_SIZE = 50
DEFAULT_CACHE_TTL = 300


def _mask_webhook_url(url: str) -> str:
    """
    Маскирует вебхук Битрикс24 для безопасного логирования.

    Args:
        url: URL вебхука для маскирования

    Returns:
        Замаскированная версия URL или "***" если URL пустой
    """
    if not url or len(url) < 30:
        return "***"
    # Показываем первые 40 символов (до токена), остальное маскируем
    return f"{url[:40]}...***"


def _sanitize_log_data(text: str, max_length: int = 500) -> str:
    """
    Удаляет потенциально чувствительные данные из логов.
    
    Маскирует:
    - Токены в URL Битрикс24
    - Email адреса
    - Телефонные номера
    
    Args:
        text: Текст для санитизации
        max_length: Максимальная длина возвращаемого текста
        
    Returns:
        Очищенный текст
    """
    if not text:
        return ""
    
    sanitized = text
    
    # Маскируем токены в URL Битрикс24
    sanitized = re.sub(
        r'(bitrix24\.[a-z]+/rest/\d+/)[a-zA-Z0-9]+',
        r'\1***',
        sanitized
    )
    
    # Маскируем email
    sanitized = re.sub(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        '***@***.***',
        sanitized
    )
    
    # Маскируем телефоны (российские и международные)
    sanitized = re.sub(
        r'(\+?\d[\d\s()\-]{8,}\d)',
        '***-***-****',
        sanitized
    )
    
    return sanitized[:max_length]


class RateLimiter:
    """
    Ограничитель запросов на основе алгоритма token bucket.
    
    Ограничивает количество запросов в секунду для защиты от rate limit API Битрикс24.
    Использует потокобезопасную реализацию с блокировкой при превышении лимита.
    
    Attributes:
        calls_per_second: Максимальное количество запросов в секунду
        min_interval: Минимальный интервал между запросами (секунды)
        last_calls: Очередь времен последних запросов
        lock: Блокировка для потокобезопасности
    """
    
    def __init__(self, calls_per_second: int = 2):
        """
        Инициализирует ограничитель запросов.
        
        Args:
            calls_per_second: Максимальное количество запросов в секунду (по умолчанию 2)
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_calls: deque = deque()
        self.lock = threading.Lock()
    
    def acquire(self) -> None:
        """
        Запрашивает разрешение на выполнение запроса к API.
        
        Блокирует выполнение текущего потока, если превышен лимит запросов.
        Использует скользящее окно в 1 секунду для подсчёта запросов.
        
        Пример:
            >>> limiter = RateLimiter(calls_per_second=5)
            >>> limiter.acquire()  # Ждёт если необходимо
            >>> # Выполнение запроса
        """
        with self.lock:
            now = datetime.now()
            
            # Удаляем старые вызовы (старше 1 секунды)
            while self.last_calls and now - self.last_calls[0] > timedelta(seconds=1):
                self.last_calls.popleft()
            
            # Если превышен лимит - ждём
            if len(self.last_calls) >= self.calls_per_second:
                sleep_time = (self.last_calls[0] + timedelta(seconds=1) - now).total_seconds()
                if sleep_time > 0:
                    logger.debug(f"Rate limiter: ожидание {sleep_time:.3f} сек")
                    time.sleep(sleep_time)
                    now = datetime.now()
            
            self.last_calls.append(now)


class BitrixWebhookClient:
    """
    Клиент для работы с Битрикс24 через вебхук.

    Attributes:
        webhook_url (str): URL вебхука
        _timeout (int): Таймаут запросов
        _max_retries (int): Максимум попыток
        _backoff_factor (float): Множитель задержки
        _session (requests.Session): Сессия с retry logic
        _managers_cache (dict): Кэш менеджеров
        _managers_cache_time (float): Время кэширования
        _cache_ttl (int): Время жизни кэша (секунды)
    """

    def __init__(
        self, webhook_url: str, max_retries: int = 3, backoff_factor: float = 1.0
    ):
        """
        Инициализация клиента.

        Args:
            webhook_url: URL вебхука Битрикс24
            max_retries: Максимальное количество попыток при временных ошибках
            backoff_factor: Множитель задержки между попытками (секунды)
        """
        self.webhook_url = webhook_url.rstrip("/")
        self._timeout = DEFAULT_TIMEOUT  # таймаут запросов в секундах
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

        # Читаем настройку rate limiting из переменных окружения
        calls_per_second = int(get_env_var("BITRIX_API_CALLS_PER_SECOND", "2"))
        
        # Инициализируем rate limiter
        self._rate_limiter = RateLimiter(calls_per_second=calls_per_second)
        logger.info(f"Rate limiter инициализирован: {calls_per_second} запросов/сек")

        # Настраиваем сессию с retry logic
        self._session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # Временные ошибки
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        # Кэш для менеджеров
        self._managers_cache = None
        self._managers_cache_time = 0
        self._cache_ttl = DEFAULT_CACHE_TTL  # 5 минут

        logger.info(
            f"Инициализация клиента для URL: {_mask_webhook_url(self.webhook_url)} (max_retries={max_retries})"
        )

    def _make_request(
        self, method: str, params: dict | None = None, log_response: bool = True
    ) -> dict | list | None:
        """
        Выполняет запрос к API Битрикс24 с retry logic для временных ошибок.

        Args:
            method: Метод API (например, 'crm.lead.list')
            params: Параметры запроса
            log_response: Логировать ответ

        Returns:
            Результат запроса или None при ошибке
        """
        # Ждём разрешения от rate limiter (блокирует при превышении лимита)
        self._rate_limiter.acquire()
        
        # Для входящих вебхуков Битрикс24 использует GET с параметром method
        url = f"{self.webhook_url}/{method}"

        logger.info(f"Запрос к методу: {method}")
        logger.debug(f"URL: {_sanitize_log_data(url)}")
        logger.debug(f"Параметры: {_sanitize_log_data(str(params))}")

        try:
            # Используем сессию с retry logic
            response = self._session.get(url, params=params, timeout=self._timeout)

            logger.info(f"Статус ответа: {response.status_code}")
            logger.debug(f"Заголовки: {dict(response.headers)}")

            if log_response:
                logger.debug(
                    f"Тело ответа: {_sanitize_log_data(response.text)}..."
                )  # Первые 500 символов

            response.raise_for_status()
            result = response.json()

            logger.debug(f"Распарсенный JSON: {type(result)}")

            # Проверяем на наличие ошибки
            if isinstance(result, dict) and result.get("error"):
                error_msg = result.get("error_description", result.get("error"))
                logger.error(f"Ошибка Битрикс24: {error_msg}")
                raise BitrixWebhookConnectionError(f"Ошибка Битрикс24: {error_msg}")

            return result.get("result") if isinstance(result, dict) else result

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP ошибка {e.response.status_code} при запросе {url}:\n"
                f"Тело ответа: {_sanitize_log_data(e.response.text)}"
            )
            if e.response.status_code == 404:
                raise BitrixWebhookNotFoundError(
                    f"Вебхук не найден (404). Проверьте:\n"
                    f"1. Вебхук активен в Битрикс24\n"
                    f"2. URL скопирован полностью\n"
                    f"3. У вебхука есть права на 'crm' и 'user'\n"
                    f"\nДетали: {_sanitize_log_data(e.response.text)}"
                ) from e
            elif e.response.status_code == 403:
                raise BitrixWebhookForbiddenError(
                    f"Недостаточно прав (403). Для работы метода '{method}'\n"
                    f"необходимы права доступа. Пересоздайте вебхук с правами:\n"
                    f"  ☑ crm (чтение)\n"
                    f"  ☑ user (чтение)\n"
                    f"\nДетали: {_sanitize_log_data(e.response.text)}"
                ) from e
            elif e.response.status_code == 429:
                raise BitrixWebhookRateLimitError(
                    f"Превышен лимит запросов (429) для {method}"
                ) from e
            else:
                raise BitrixWebhookConnectionError(
                    f"HTTP ошибка {e.response.status_code} для {method}"
                ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения: {e}")
            raise BitrixWebhookConnectionError(
                f"Ошибка подключения к Битрикс24: {e}"
            ) from e
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Полученный ответ: {_sanitize_log_data(response.text)}")
            raise BitrixWebhookConnectionError(
                f"Ошибка парсинга ответа: {e}\nОтвет: {_sanitize_log_data(response.text)}"
            ) from e

    def _iter_paginated(
        self,
        method: str,
        params: dict | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        log_response: bool = False,
    ) -> Iterable[list[dict]]:
        start = 0
        while True:
            request_params = dict(params or {})
            request_params["start"] = start
            result = self._make_request(method, request_params, log_response=log_response)
            items = result if isinstance(result, list) else []
            if not items:
                break
            yield items
            if len(items) < batch_size:
                break
            start += batch_size

    def test_connection(self) -> tuple[bool, str]:
        """
        Проверяет подключение к Битрикс24.

        Returns:
            Кортеж (успех, сообщение)
        """
        logger.info("=== Начало проверки подключения ===")

        try:
            # Пробуем простой метод для проверки
            logger.info("Вызов метода user.current...")
            result = self._make_request("user.current", log_response=True)

            logger.info(f"Результат: {result is not None}")

            if result is not None:
                user_name = result.get("NAME", "") + " " + result.get("LAST_NAME", "")
                user_id = result.get("ID", "")
                logger.info(f"Подключено как: {user_name} (ID: {user_id})")
                return True, f"Подключено как {user_name.strip()} (ID: {user_id})"
            else:
                logger.warning("Пустой результат от user.current")
                return False, "Ошибка авторизации или неверный вебхук"

        except BitrixWebhookError as e:
            logger.error(f"BitrixWebhookError: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False, f"Неизвестная ошибка: {type(e).__name__}: {str(e)}"

    def get_new_leads_by_manager(
        self, status_id: str = "NEW", max_leads: int = 500
    ) -> dict[int, int]:
        """
        Получает количество новых лидов по менеджерам.

        Args:
            status_id: ID статуса лида (по умолчанию "NEW" = "Новая заявка")
            max_leads: Максимальное количество лидов для обработки

        Returns:
            Словарь {manager_id: count}
        """
        logger.info(
            f"Получение лидов по менеджерам для статуса: {status_id} (макс. {max_leads})"
        )

        leads_count = {}
        total_leads = 0

        for items in self._iter_paginated(
            "crm.lead.list",
            {"select": ["ASSIGNED_BY_ID"], "filter[STATUS_ID]": status_id},
            batch_size=DEFAULT_BATCH_SIZE,
            log_response=False,
        ):
            for lead in items:
                manager_id = lead.get("ASSIGNED_BY_ID")
                if manager_id:
                    leads_count[int(manager_id)] = (
                        leads_count.get(int(manager_id), 0) + 1
                    )
                    total_leads += 1

            logger.debug(f"Обработано {len(items)} лидов, всего: {total_leads}")

            # Останавливаемся если достигли лимита
            if total_leads >= max_leads:
                logger.info(f"Достигнут лимит лидов: {max_leads}")
                break

        logger.info(f"Всего лидов: {total_leads}, менеджеров: {len(leads_count)}")
        return leads_count

    def get_managers(self) -> dict[int, str]:
        """
        Получает список менеджеров (пользователей) из Битрикс24.

        Использует кэширование для уменьшения количества API запросов.

        Returns:
            Словарь {user_id: full_name}
        """
        try:
            # Проверяем кэш
            current_time = time.time()
            if (
                hasattr(self, "_managers_cache")
                and self._managers_cache is not None
                and hasattr(self, "_managers_cache_time")
                and current_time - self._managers_cache_time < self._cache_ttl
            ):
                logger.debug("Используем кэш менеджеров")
                return self._managers_cache
        except Exception as e:
            logger.error(f"Ошибка проверки кэша: {type(e).__name__}: {e}")
            # Сбрасываем кэш при ошибке
            self._managers_cache = None
            self._managers_cache_time = 0

        logger.info("Получение списка менеджеров...")

        managers = {}
        try:
            for users in self._iter_paginated(
                "user.get",
                {"filter": {"ACTIVE": True}},
                batch_size=DEFAULT_BATCH_SIZE,
                log_response=False,
            ):
                for user in users:
                    try:
                        user_id = user.get("ID")
                        # Формируем полное имя
                        last_name = user.get("LAST_NAME", "")
                        first_name = user.get("NAME", "")
                        full_name = f"{last_name} {first_name}".strip()

                        if user_id and full_name:
                            managers[int(user_id)] = full_name
                            logger.debug(
                                f"Добавлен менеджер: {full_name} (ID: {user_id})"
                            )
                    except Exception as e:
                        logger.warning(f"Ошибка обработки пользователя: {e}")
                        continue
        except Exception as e:
            logger.error(f"Ошибка при загрузке менеджеров: {type(e).__name__}: {e}")

        logger.info(f"Всего менеджеров: {len(managers)}")

        # Кэшируем результат
        try:
            self._managers_cache = managers
            self._managers_cache_time = time.time()
            logger.debug(
                f"Менеджеры закэшированы, кэш действителен до {self._managers_cache_time + self._cache_ttl}"
            )
        except Exception as e:
            logger.error(f"Ошибка кэширования: {type(e).__name__}: {e}")

        return managers

    def get_lead_statuses(self) -> dict[str, str]:
        """
        Получает список статусов лидов.

        Returns:
            Словарь {status_id: status_name}
        """
        logger.info("Получение списка статусов лидов...")

        result = self._make_request("crm.status.list", {"entityId": "STATUS_ID"})

        statuses = {}
        if result:
            for status in result:
                status_id = status.get("STATUS_ID")
                name = status.get("NAME")
                if status_id and name:
                    statuses[status_id] = name
                    logger.debug(f"Статус: {status_id} = {name}")

        logger.info(f"Найдено статусов: {len(statuses)}")
        return statuses


def get_leads_distribution(
    webhook_url: str,
    status_name: str = "Новая заявка",
    max_leads: int = 500,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> tuple[dict[str, str], dict[str, int], bool]:
    """
    Получает распределение лидов по менеджерам с именами.

    Args:
        webhook_url: URL вебхука
        status_name: Название статуса (по умолчанию "Новая заявка")
        max_leads: Максимальное количество лидов для обработки
        max_retries: Максимальное количество попыток при временных ошибках
        backoff_factor: Множитель задержки между попытками (секунды)

    Returns:
        Кортеж (менеджеры, распределение лидов, успех)
    """
    logger.info(f"=== Получение распределения лидов ===")
    logger.info(f"URL: {_mask_webhook_url(webhook_url)}")
    logger.info(f"Статус: {status_name}")
    logger.info(f"Макс. лидов: {max_leads}")

    try:
        client = BitrixWebhookClient(
            webhook_url, max_retries=max_retries, backoff_factor=backoff_factor
        )

        # Получаем список статусов для нахождения ID
        logger.info("Получение списка статусов...")
        statuses = client.get_lead_statuses()
        status_id = "NEW"  # по умолчанию

        logger.info(f"Найдено статусов: {len(statuses)}")
        for sid, sname in statuses.items():
            if sname == status_name:
                status_id = sid
                logger.info(f"Найден статус '{status_name}' -> ID: {status_id}")
                break

        # Получаем менеджеров
        logger.info("Получение списка менеджеров...")
        managers_raw = client.get_managers()

        # Получаем распределение лидов
        logger.info(f"Получение лидов для статуса '{status_id}' (макс. {max_leads})...")
        leads_by_id = client.get_new_leads_by_manager(status_id, max_leads=max_leads)

        # Преобразуем ID в имена
        managers = {}
        leads_distribution = {}

        for manager_id, name in managers_raw.items():
            managers[name] = manager_id
            leads_distribution[name] = leads_by_id.get(manager_id, 0)

        logger.info(
            f"Успешно! Менеджеров: {len(managers)}, лидов распределено: {sum(leads_distribution.values())}"
        )
        return managers, leads_distribution, True

    except Exception as e:
        logger.error(f"Ошибка: {type(e).__name__}: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return {}, {}, False
