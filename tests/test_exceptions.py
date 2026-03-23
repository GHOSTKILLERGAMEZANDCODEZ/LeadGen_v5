"""
Модульные тесты для иерархии исключений LeadGen v5.

Проверяет:
- Иерархию наследования исключений
- Создание исключений с сообщениями
- Цепочку исключений (original_exception)
- Ловлю исключений через базовые классы
"""

import unittest
from modules.exceptions import (
    LeadGenError,
    SecurityError,
    BitrixWebhookError,
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookInvalidURLError,
    BitrixWebhookConnectionError,
    ProcessingError,
    ValidationError,
    ExportError,
)


class TestExceptionsHierarchy(unittest.TestCase):
    """Тестирует иерархию наследования исключений."""

    def test_all_exceptions_inherit_from_leadgen_error(self):
        """Все исключения наследуются от LeadGenError."""
        self.assertTrue(issubclass(SecurityError, LeadGenError))
        self.assertTrue(issubclass(BitrixWebhookError, LeadGenError))
        self.assertTrue(issubclass(ProcessingError, LeadGenError))
        self.assertTrue(issubclass(ValidationError, LeadGenError))
        self.assertTrue(issubclass(ExportError, LeadGenError))

    def test_bitrix_exceptions_inherit_from_bitrix_webhook_error(self):
        """Все Bitrix-исключения наследуются от BitrixWebhookError."""
        self.assertTrue(issubclass(BitrixWebhookNotFoundError, BitrixWebhookError))
        self.assertTrue(issubclass(BitrixWebhookForbiddenError, BitrixWebhookError))
        self.assertTrue(issubclass(BitrixWebhookRateLimitError, BitrixWebhookError))
        self.assertTrue(issubclass(BitrixWebhookInvalidURLError, BitrixWebhookError))
        self.assertTrue(issubclass(BitrixWebhookConnectionError, BitrixWebhookError))

    def test_bitrix_webhook_error_inherit_from_leadgen_error(self):
        """BitrixWebhookError наследуется от LeadGenError."""
        self.assertTrue(issubclass(BitrixWebhookError, LeadGenError))


class TestExceptionsCreation(unittest.TestCase):
    """Тестирует создание исключений."""

    def test_exception_with_message(self):
        """Создание исключения с сообщением."""
        error = BitrixWebhookNotFoundError("Вебхук не найден")
        self.assertEqual(str(error), "Вебхук не найден")

    def test_exception_with_original_exception(self):
        """Создание исключения с оригинальным исключением."""
        original = ValueError("Original error")
        error = BitrixWebhookConnectionError("Connection failed", original)
        self.assertEqual(error.message, "Connection failed")
        self.assertEqual(error.original_exception, original)

    def test_exception_str_with_original(self):
        """Строковое представление с оригинальным исключением."""
        original = ValueError("Original error")
        error = BitrixWebhookConnectionError("Connection failed", original)
        error_str = str(error)
        self.assertIn("Connection failed", error_str)
        self.assertIn("Original error", error_str)

    def test_exception_str_without_original(self):
        """Строковое представление без оригинального исключения."""
        error = BitrixWebhookNotFoundError("Вебхук не найден")
        self.assertEqual(str(error), "Вебхук не найден")


class TestExceptionsCatching(unittest.TestCase):
    """Тестирует ловлю исключений через базовые классы."""

    def test_catch_bitrix_error_by_base_class(self):
        """Ловля BitrixWebhookNotFoundError через BitrixWebhookError."""
        caught = False
        try:
            raise BitrixWebhookNotFoundError("404")
        except BitrixWebhookError as e:
            caught = True
            self.assertIsInstance(e, BitrixWebhookNotFoundError)
        self.assertTrue(caught)

    def test_catch_all_bitrix_exceptions(self):
        """Ловля всех Bitrix-исключений через BitrixWebhookError."""
        exceptions = [
            BitrixWebhookNotFoundError("404"),
            BitrixWebhookForbiddenError("403"),
            BitrixWebhookRateLimitError("429"),
            BitrixWebhookInvalidURLError("Invalid URL"),
            BitrixWebhookConnectionError("Connection error"),
        ]
        
        for exc in exceptions:
            caught = False
            try:
                raise exc
            except BitrixWebhookError as e:
                caught = True
                self.assertEqual(str(e), str(exc))
            self.assertTrue(caught)

    def test_catch_all_leadgen_exceptions(self):
        """Ловля всех исключений через LeadGenError."""
        exceptions = [
            SecurityError("Security error"),
            BitrixWebhookNotFoundError("404"),
            ProcessingError("Processing error"),
            ValidationError("Validation error"),
            ExportError("Export error"),
        ]
        
        for exc in exceptions:
            caught = False
            try:
                raise exc
            except LeadGenError as e:
                caught = True
                self.assertEqual(str(e), str(exc))
            self.assertTrue(caught)


class TestSpecificExceptions(unittest.TestCase):
    """Тестирует специфичные сценарии для каждого типа исключений."""

    def test_bitrix_webhook_not_found(self):
        """BitrixWebhookNotFoundError для 404."""
        with self.assertRaises(BitrixWebhookNotFoundError) as context:
            raise BitrixWebhookNotFoundError("Вебхук не найден (404)")
        self.assertIn("404", str(context.exception))

    def test_bitrix_webhook_forbidden(self):
        """BitrixWebhookForbiddenError для 403."""
        with self.assertRaises(BitrixWebhookForbiddenError) as context:
            raise BitrixWebhookForbiddenError("Недостаточно прав (403)")
        self.assertIn("403", str(context.exception))

    def test_bitrix_webhook_rate_limit(self):
        """BitrixWebhookRateLimitError для 429."""
        with self.assertRaises(BitrixWebhookRateLimitError) as context:
            raise BitrixWebhookRateLimitError("Превышен лимит (429)")
        self.assertIn("429", str(context.exception))

    def test_bitrix_webhook_invalid_url(self):
        """BitrixWebhookInvalidURLError для неверного URL."""
        with self.assertRaises(BitrixWebhookInvalidURLError) as context:
            raise BitrixWebhookInvalidURLError("Неверный формат URL")
        self.assertIn("URL", str(context.exception))

    def test_bitrix_webhook_connection_error(self):
        """BitrixWebhookConnectionError для ошибок подключения."""
        with self.assertRaises(BitrixWebhookConnectionError) as context:
            raise BitrixWebhookConnectionError("Ошибка подключения")
        self.assertIn("подключения", str(context.exception))

    def test_security_error(self):
        """SecurityError для ошибок безопасности."""
        with self.assertRaises(SecurityError) as context:
            raise SecurityError("Path Traversal обнаружен")
        self.assertIn("Path Traversal", str(context.exception))

    def test_processing_error(self):
        """ProcessingError для ошибок обработки."""
        with self.assertRaises(ProcessingError) as context:
            raise ProcessingError("Ошибка обработки файла")
        self.assertIn("обработки", str(context.exception))

    def test_validation_error(self):
        """ValidationError для ошибок валидации."""
        with self.assertRaises(ValidationError) as context:
            raise ValidationError("Неверный формат телефона")
        self.assertIn("формат", str(context.exception))

    def test_export_error(self):
        """ExportError для ошибок экспорта."""
        with self.assertRaises(ExportError) as context:
            raise ExportError("Ошибка записи CSV")
        self.assertIn("записи", str(context.exception))


if __name__ == "__main__":
    unittest.main()
