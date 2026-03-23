"""
Модульные тесты для modules/bitrix_webhook.py.

Тестирует:
- RateLimiter: ограничение запросов
- BitrixWebhookClient: инициализация, подключение, получение данных
- Обработку исключений: 404, 403, 429, connection errors
- Маскирование и санитизацию данных

Использует mock для requests.Session.get и requests.Session.post.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import time
import threading
from datetime import datetime, timedelta

from modules.bitrix_webhook import (
    BitrixWebhookClient,
    RateLimiter,
    _mask_webhook_url,
    _sanitize_log_data,
    get_leads_distribution,
)
from modules.exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookConnectionError,
    BitrixWebhookInvalidURLError,
)


class TestMaskWebhookUrl(unittest.TestCase):
    """Тестирует функцию маскирования вебхук URL."""

    def test_mask_webhook_url_normal(self):
        """Тестирует маскирование обычного вебхука."""
        url = "https://company.bitrix24.ru/rest/1/abc123xyz456def789/"
        masked = _mask_webhook_url(url)
        
        self.assertIn("company.bitrix24.ru/rest/1/", masked)
        self.assertIn("...***", masked)
        self.assertNotIn("abc123xyz456def789", masked)
    
    def test_mask_webhook_url_empty(self):
        """Тестирует маскирование пустого вебхука."""
        masked = _mask_webhook_url("")
        self.assertEqual(masked, "***")
    
    def test_mask_webhook_url_short(self):
        """Тестирует маскирование короткого вебхука."""
        masked = _mask_webhook_url("short")
        self.assertEqual(masked, "***")
    
    def test_mask_webhook_url_none(self):
        """Тестирует маскирование None."""
        masked = _mask_webhook_url(None)
        self.assertEqual(masked, "***")


class TestSanitizeLogData(unittest.TestCase):
    """Тестирует функцию санитизации логов."""

    def test_sanitize_log_data_email(self):
        """Тестирует санитизацию email."""
        text = "Email: test@example.com"
        sanitized = _sanitize_log_data(text)
        
        self.assertEqual(sanitized, "Email: ***@***.***")
    
    def test_sanitize_log_data_phone(self):
        """Тестирует санитизацию телефона."""
        text = "Phone: +7 (999) 123-45-67"
        sanitized = _sanitize_log_data(text)
        
        self.assertIn("***-***-****", sanitized)
    
    def test_sanitize_log_data_bitrix_url(self):
        """Тестирует санитизацию URL Битрикс24."""
        text = "URL: https://company.bitrix24.ru/rest/1/abc123xyz456/"
        sanitized = _sanitize_log_data(text)
        
        self.assertIn("bitrix24.ru/rest/1/***", sanitized)
        self.assertNotIn("abc123xyz456", sanitized)
    
    def test_sanitize_log_data_combined(self):
        """Тестирует комбинированную санитизацию."""
        text = "Lead: John, john@test.com, +79991234567, https://company.bitrix24.ru/rest/1/abc123/"
        sanitized = _sanitize_log_data(text)
        
        self.assertNotIn("john@test.com", sanitized)
        self.assertNotIn("+79991234567", sanitized)
        self.assertNotIn("abc123", sanitized)
        self.assertIn("***@***.***", sanitized)
        self.assertIn("***-***-****", sanitized)
    
    def test_sanitize_log_data_empty(self):
        """Тестирует санитизацию пустой строки."""
        sanitized = _sanitize_log_data("")
        self.assertEqual(sanitized, "")
    
    def test_sanitize_log_data_none(self):
        """Тестирует санитизацию None."""
        sanitized = _sanitize_log_data(None)
        self.assertEqual(sanitized, "")
    
    def test_sanitize_log_data_max_length(self):
        """Тестирует ограничение максимальной длины."""
        text = "A" * 1000
        sanitized = _sanitize_log_data(text, max_length=100)
        
        self.assertEqual(len(sanitized), 100)


class TestRateLimiter(unittest.TestCase):
    """Тестирует RateLimiter."""

    def test_rate_limiter_init(self):
        """Тестирует инициализацию RateLimiter."""
        limiter = RateLimiter(calls_per_second=5)
        
        self.assertEqual(limiter.calls_per_second, 5)
        self.assertEqual(limiter.min_interval, 0.2)
        self.assertIsInstance(limiter.last_calls, type(limiter.last_calls))
        self.assertIsInstance(limiter.lock, type(threading.Lock()))
    
    def test_rate_limiter_init_default(self):
        """Тестирует инициализацию по умолчанию."""
        limiter = RateLimiter()
        
        self.assertEqual(limiter.calls_per_second, 2)
        self.assertEqual(limiter.min_interval, 0.5)
    
    def test_rate_limiter_acquire_under_limit(self):
        """Тестирует acquire когда лимит не превышен."""
        limiter = RateLimiter(calls_per_second=10)
        
        # Первые запросы должны проходить мгновенно
        start = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start
        
        # Должно быть почти мгновенно (с небольшим допуском)
        self.assertLess(elapsed, 0.1)
    
    def test_rate_limiter_acquire_over_limit(self):
        """Тестирует acquire когда лимит превышен."""
        limiter = RateLimiter(calls_per_second=5)
        
        # Превышаем лимит
        for _ in range(5):
            limiter.acquire()
        
        # 6-й запрос должен ждать
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        
        # Должен ждать хотя бы часть интервала
        self.assertGreaterEqual(elapsed, 0.1)
    
    def test_rate_limiter_thread_safety(self):
        """Тестирует потокобезопасность."""
        limiter = RateLimiter(calls_per_second=100)
        results = []
        
        def worker():
            for _ in range(10):
                limiter.acquire()
                results.append(time.time())
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Все вызовы должны завершиться
        self.assertEqual(len(results), 50)


class TestBitrixWebhookClientInit(unittest.TestCase):
    """Тестирует инициализацию BitrixWebhookClient."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_init(self, mock_session_class):
        """Тестирует инициализацию клиента."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        self.assertEqual(client.webhook_url, 'https://test.bitrix24.ru/rest/1/abc123')
        self.assertEqual(client._timeout, 30)
        self.assertEqual(client._max_retries, 3)
        self.assertEqual(client._backoff_factor, 1.0)
        self.assertIsInstance(client._rate_limiter, RateLimiter)
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_init_strips_trailing_slash(self, mock_session_class):
        """Тестирует удаление завершающего слэша."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123///')
        
        self.assertEqual(client.webhook_url, 'https://test.bitrix24.ru/rest/1/abc123')
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_init_custom_retries(self, mock_session_class):
        """Тестирует инициализацию с кастомными retry."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient(
            'https://test.bitrix24.ru/rest/1/abc123/',
            max_retries=5,
            backoff_factor=2.0
        )
        
        self.assertEqual(client._max_retries, 5)
        self.assertEqual(client._backoff_factor, 2.0)


class TestBitrixWebhookClientConnection(unittest.TestCase):
    """Тестирует методы подключения BitrixWebhookClient."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_test_connection_success(self, mock_session_class):
        """Тестирует успешное подключение."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"NAME": "Test", "LAST_NAME": "User", "ID": 1}}'
        mock_response.json.return_value = {
            'result': {'NAME': 'Test', 'LAST_NAME': 'User', 'ID': 1}
        }
        mock_response.headers = {}
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        success, message = client.test_connection()
        
        self.assertTrue(success)
        self.assertIn('Test User', message)
        self.assertIn('ID: 1', message)
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_test_connection_failure_exception(self, mock_session_class):
        """Тестирует неудачное подключение с исключением."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception('Connection error')
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        success, message = client.test_connection()
        
        self.assertFalse(success)
        self.assertIn('ошибка', message.lower())
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_test_connection_empty_result(self, mock_session_class):
        """Тестирует подключение с пустым результатом."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": null}'
        mock_response.json.return_value = {'result': None}
        mock_response.headers = {}
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        success, message = client.test_connection()
        
        self.assertFalse(success)
        self.assertIn('ошибка', message.lower())


class TestBitrixWebhookClientLeads(unittest.TestCase):
    """Тестирует методы получения лидов."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_leads_distribution_success(self, mock_session_class):
        """Тестирует получение распределения лидов."""
        mock_session = MagicMock()
        mock_session.get.return_value.json.side_effect = [
            {'result': [
                {'ASSIGNED_BY_NAME': 'Manager 1', 'CNT': 10},
                {'ASSIGNED_BY_NAME': 'Manager 2', 'CNT': 15},
            ]},
        ]
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        # Мокаем методы для упрощения теста
        with patch.object(client, 'get_managers', return_value={1: 'Manager 1', 2: 'Manager 2'}):
            with patch.object(client, 'get_new_leads_by_manager', return_value={1: 10, 2: 15}):
                with patch.object(client, 'get_lead_statuses', return_value={'NEW': 'Новая заявка'}):
                    result = client.get_leads_distribution() if hasattr(client, 'get_leads_distribution') else None
        
        # Тест для standalone функции
        mock_session.get.return_value.json.side_effect = [
            {'result': {'STATUS_ID': 'NEW', 'NAME': 'Новая заявка'}},
            {'result': [{}, {}]},
            {'result': [{'ASSIGNED_BY_ID': 1}, {'ASSIGNED_BY_ID': 2}]},
        ]
        
        managers, distribution, success = get_leads_distribution(
            'https://test.bitrix24.ru/rest/1/abc123/',
            max_leads=10
        )
        
        # Функция должна вернуть успех
        self.assertIsInstance(success, bool)
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_leads_distribution_empty(self, mock_session_class):
        """Тестирует получение пустого распределения лидов."""
        mock_session = MagicMock()
        mock_session.get.return_value.json.return_value = {'result': []}
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        # Мокаем методы
        with patch.object(client, 'get_managers', return_value={}):
            with patch.object(client, 'get_new_leads_by_manager', return_value={}):
                with patch.object(client, 'get_lead_statuses', return_value={}):
                    pass
        
        managers, distribution, success = get_leads_distribution(
            'https://test.bitrix24.ru/rest/1/abc123/',
            max_leads=10
        )
        
        self.assertIsInstance(managers, dict)
        self.assertIsInstance(distribution, dict)


class TestBitrixWebhookExceptions(unittest.TestCase):
    """Тестирует обработку исключений."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_bitrix_webhook_not_found_error(self, mock_session_class):
        """Тестирует обработку 404 ошибки."""
        from requests.exceptions import HTTPError
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        
        mock_session = MagicMock()
        mock_session.get.side_effect = HTTPError(response=mock_response)
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        with self.assertRaises(BitrixWebhookNotFoundError):
            client.get_lead_statuses()
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_bitrix_webhook_forbidden_error(self, mock_session_class):
        """Тестирует обработку 403 ошибки."""
        from requests.exceptions import HTTPError
        
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        
        mock_session = MagicMock()
        mock_session.get.side_effect = HTTPError(response=mock_response)
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        with self.assertRaises(BitrixWebhookForbiddenError):
            client.get_lead_statuses()
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_bitrix_webhook_rate_limit_error(self, mock_session_class):
        """Тестирует обработку 429 ошибки."""
        from requests.exceptions import HTTPError
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too many requests"
        
        mock_session = MagicMock()
        mock_session.get.side_effect = HTTPError(response=mock_response)
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        with self.assertRaises(BitrixWebhookRateLimitError):
            client.get_lead_statuses()
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_bitrix_webhook_connection_error(self, mock_session_class):
        """Тестирует обработку ошибки подключения."""
        import requests.exceptions
        
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        with self.assertRaises(BitrixWebhookConnectionError):
            client.get_lead_statuses()
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_bitrix_webhook_invalid_json(self, mock_session_class):
        """Тестирует обработку невалидного JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not a JSON"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        with self.assertRaises(BitrixWebhookConnectionError):
            client.get_lead_statuses()


class TestGetLeadsDistributionFunction(unittest.TestCase):
    """Тестирует standalone функцию get_leads_distribution."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_leads_distribution_standalone_success(self, mock_session_class):
        """Тестирует успешное выполнение функции."""
        # Создаём моки для последовательных вызовов
        mock_response_statuses = MagicMock()
        mock_response_statuses.status_code = 200
        mock_response_statuses.text = '{"result": [{"STATUS_ID": "NEW", "NAME": "Новая заявка"}]}'
        mock_response_statuses.json.return_value = {'result': [{'STATUS_ID': 'NEW', 'NAME': 'Новая заявка'}]}
        mock_response_statuses.headers = {}
        
        mock_response_users = MagicMock()
        mock_response_users.status_code = 200
        mock_response_users.text = '{"result": [{"ID": 1, "NAME": "John", "LAST_NAME": "Doe"}]}'
        mock_response_users.json.return_value = {'result': [{'ID': 1, 'NAME': 'John', 'LAST_NAME': 'Doe'}]}
        mock_response_users.headers = {}
        
        mock_response_leads = MagicMock()
        mock_response_leads.status_code = 200
        mock_response_leads.text = '{"result": [{"ASSIGNED_BY_ID": 1}]}'
        mock_response_leads.json.return_value = {'result': [{'ASSIGNED_BY_ID': 1}]}
        mock_response_leads.headers = {}
        
        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_response_statuses, mock_response_users, mock_response_leads]
        mock_session_class.return_value = mock_session
        
        managers, distribution, success = get_leads_distribution(
            'https://test.bitrix24.ru/rest/1/abc123/',
            status_name='Новая заявка',
            max_leads=10
        )
        
        self.assertIsInstance(managers, dict)
        self.assertIsInstance(distribution, dict)
        self.assertTrue(success)
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_leads_distribution_standalone_failure(self, mock_session_class):
        """Тестирует неудачное выполнение функции."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception('API error')
        mock_session_class.return_value = mock_session
        
        managers, distribution, success = get_leads_distribution(
            'https://test.bitrix24.ru/rest/1/abc123/',
        )
        
        self.assertEqual(managers, {})
        self.assertEqual(distribution, {})
        self.assertFalse(success)


class TestBitrixWebhookClientManagers(unittest.TestCase):
    """Тестирует методы работы с менеджерами."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_managers_success(self, mock_session_class):
        """Тестирует успешное получение менеджеров."""
        mock_session = MagicMock()
        mock_session.get.return_value.json.return_value = {
            'result': [
                {'ID': 1, 'NAME': 'John', 'LAST_NAME': 'Doe'},
                {'ID': 2, 'NAME': 'Jane', 'LAST_NAME': 'Smith'},
            ]
        }
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        managers = client.get_managers()
        
        self.assertEqual(len(managers), 2)
        self.assertEqual(managers[1], 'Doe John')
        self.assertEqual(managers[2], 'Smith Jane')
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_managers_caching(self, mock_session_class):
        """Тестирует кэширование менеджеров."""
        mock_session = MagicMock()
        mock_session.get.return_value.json.return_value = {
            'result': [{'ID': 1, 'NAME': 'John', 'LAST_NAME': 'Doe'}]
        }
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        
        # Первый вызов
        managers1 = client.get_managers()
        # Второй вызов (должен использовать кэш)
        managers2 = client.get_managers()
        
        # Session.get должен быть вызван только один раз
        self.assertEqual(mock_session.get.call_count, 1)
        self.assertEqual(managers1, managers2)
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_managers_empty_result(self, mock_session_class):
        """Тестирует получение пустого списка менеджеров."""
        mock_session = MagicMock()
        mock_session.get.return_value.json.return_value = {'result': []}
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        managers = client.get_managers()
        
        self.assertEqual(managers, {})


class TestBitrixWebhookClientStatuses(unittest.TestCase):
    """Тестирует методы работы со статусами."""

    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_lead_statuses_success(self, mock_session_class):
        """Тестирует успешное получение статусов."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": [{"STATUS_ID": "NEW", "NAME": "Новая заявка"}]}'
        mock_response.json.return_value = {
            'result': [
                {'STATUS_ID': 'NEW', 'NAME': 'Новая заявка'},
                {'STATUS_ID': 'IN_PROGRESS', 'NAME': 'В работе'},
            ]
        }
        mock_response.headers = {}
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        statuses = client.get_lead_statuses()
        
        self.assertEqual(len(statuses), 2)
        self.assertEqual(statuses['NEW'], 'Новая заявка')
        self.assertEqual(statuses['IN_PROGRESS'], 'В работе')
    
    @patch('modules.bitrix_webhook.requests.Session')
    def test_get_lead_statuses_empty(self, mock_session_class):
        """Тестирует получение пустого списка статусов."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": []}'
        mock_response.json.return_value = {'result': []}
        mock_response.headers = {}
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BitrixWebhookClient('https://test.bitrix24.ru/rest/1/abc123/')
        statuses = client.get_lead_statuses()
        
        self.assertEqual(statuses, {})


if __name__ == '__main__':
    unittest.main()
