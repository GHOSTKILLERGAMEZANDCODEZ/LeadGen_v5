"""
Тесты для модуля phone_validator.
"""

import unittest
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импорт для тестов
from modules.phone_validator import clean_phone, validate_phone, format_phone


class TestPhoneValidator(unittest.TestCase):
    """Тесты валидатора телефонов."""
    
    def test_clean_phone_valid_russian(self):
        """Проверка корректных российских номеров."""
        self.assertEqual(clean_phone("79991234567"), "79991234567")
        self.assertEqual(clean_phone("89991234567"), "79991234567")
        self.assertEqual(clean_phone("+79991234567"), "79991234567")
    
    def test_clean_phone_with_formatting(self):
        """Проверка номеров с форматированием."""
        self.assertEqual(clean_phone("+7 (999) 123-45-67"), "79991234567")
        self.assertEqual(clean_phone("8 (999) 123 45 67"), "79991234567")
        self.assertEqual(clean_phone("7-999-123-45-67"), "79991234567")
    
    def test_clean_phone_scientific_notation(self):
        """Проверка конвертации из научной нотации."""
        self.assertEqual(clean_phone("7.8005001695e+10"), "78005001695")
        self.assertEqual(clean_phone("79991234567.0"), "79991234567")
    
    def test_clean_phone_invalid_short(self):
        """Проверка отклонения коротких номеров."""
        self.assertIsNone(clean_phone("12345"))
        self.assertIsNone(clean_phone("7999123"))
    
    def test_clean_phone_invalid_prefix(self):
        """Проверка отклонения номеров с неверным префиксом."""
        self.assertIsNone(clean_phone("69991234567"))
        self.assertIsNone(clean_phone("59991234567"))
    
    def test_clean_phone_none_empty(self):
        """Проверка обработки пустых значений."""
        self.assertIsNone(clean_phone(None))
        self.assertIsNone(clean_phone(""))
        self.assertIsNone(clean_phone("nan"))
        self.assertIsNone(clean_phone("None"))
    
    def test_format_phone(self):
        """Проверка форматирования телефонов."""
        self.assertEqual(format_phone("79991234567", '7'), "79991234567")
        self.assertEqual(format_phone("79991234567", '8'), "89991234567")
        self.assertEqual(format_phone("79991234567", '+7'), "+79991234567")
    
    def test_clean_phone_with_format(self):
        """Проверка очистки с форматированием."""
        self.assertEqual(clean_phone("89991234567", phone_format='8'), "89991234567")
        self.assertEqual(clean_phone("89991234567", phone_format='+7'), "+79991234567")
        self.assertEqual(clean_phone("89991234567", phone_format='7'), "79991234567")
    
    def test_validate_phone(self):
        """Проверка функции валидации."""
        self.assertTrue(validate_phone("79991234567"))
        self.assertTrue(validate_phone("89991234567"))
        self.assertFalse(validate_phone("7999123456"))
        self.assertFalse(validate_phone(None))
        self.assertFalse(validate_phone(""))


if __name__ == "__main__":
    unittest.main()
