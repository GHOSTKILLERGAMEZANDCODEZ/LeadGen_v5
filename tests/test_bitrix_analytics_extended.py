"""
Дополнительные модульные тесты для modules/bitrix_analytics.py
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.bitrix_analytics import (
    extract_category,
    normalize_phone,
    _has_value,
    _collect_phone_set,
)


class TestBitrixAnalyticsExtended(unittest.TestCase):
    """Дополнительные тесты для аналитики Битрикс24."""
    
    # ===== extract_category =====
    
    def test_extract_category_simple(self):
        """Тестирует извлечение категории."""
        title = "Продукты / Молоко"
        category = extract_category(title)
        
        self.assertEqual(category, "Продукты / Молоко")
    
    def test_extract_category_no_separator(self):
        """Тестирует отсутствие разделителя."""
        title = "Просто название"
        category = extract_category(title)
        
        self.assertEqual(category, "Просто название")
    
    def test_extract_category_empty(self):
        """Тестирует пустую строку."""
        category = extract_category("")
        
        self.assertEqual(category, "")
    
    def test_extract_category_none(self):
        """Тестирует None."""
        category = extract_category(None)
        
        self.assertEqual(category, "")
    
    def test_extract_category_whitespace(self):
        """Тестирует с пробелами."""
        title = "  Продукты / Молоко  "
        category = extract_category(title)
        
        self.assertEqual(category, "Продукты / Молоко")
    
    def test_extract_category_with_dash(self):
        """Тестирует с разделителем -."""
        title = "Категория - Название компании"
        category = extract_category(title)
        
        self.assertEqual(category, "Категория")
    
    # ===== normalize_phone =====
    
    def test_normalize_phone_russian(self):
        """Тестирует российский номер."""
        phone = "+7 (999) 123-45-67"
        normalized = normalize_phone(phone)
        
        self.assertEqual(normalized, "79991234567")
    
    def test_normalize_phone_formatted(self):
        """Тестирует уже форматированный."""
        phone = "79991234567"
        normalized = normalize_phone(phone)
        
        self.assertEqual(normalized, "79991234567")
    
    def test_normalize_phone_empty(self):
        """Тестирует пустой номер."""
        normalized = normalize_phone("")
        
        self.assertIsNone(normalized)
    
    def test_normalize_phone_none(self):
        """Тестирует None."""
        normalized = normalize_phone(None)
        
        self.assertIsNone(normalized)
    
    def test_normalize_phone_with_spaces(self):
        """Тестирует с пробелами."""
        phone = "7 999 123 45 67"
        normalized = normalize_phone(phone)
        
        self.assertEqual(normalized, "79991234567")
    
    def test_normalize_phone_8_prefix(self):
        """Тестирует с префиксом 8."""
        phone = "8 (999) 123-45-67"
        normalized = normalize_phone(phone)
        
        self.assertEqual(normalized, "79991234567")
    
    def test_normalize_phone_10_digits(self):
        """Тестирует 10 цифр (без 7)."""
        phone = "9991234567"
        normalized = normalize_phone(phone)
        
        self.assertEqual(normalized, "79991234567")
    
    def test_normalize_phone_invalid_short(self):
        """Тестирует короткий номер."""
        phone = "12345"
        normalized = normalize_phone(phone)
        
        self.assertIsNone(normalized)
    
    # ===== _has_value =====
    
    def test_has_value_with_data(self):
        """Тестирует со значениями."""
        series = pd.Series(["value1", "value2", ""])
        result = _has_value(series)
        
        self.assertTrue(result.iloc[0])
        self.assertTrue(result.iloc[1])
        self.assertFalse(result.iloc[2])
    
    def test_has_value_with_nan(self):
        """Тестирует с NaN."""
        series = pd.Series([None, float('nan'), "value"])
        result = _has_value(series)
        
        self.assertFalse(result.iloc[0])
        self.assertFalse(result.iloc[1])
        self.assertTrue(result.iloc[2])
    
    # ===== _collect_phone_set =====
    
    def test_collect_phone_set_single(self):
        """Тестирует один телефон."""
        row = pd.Series({
            "Рабочий телефон норм": "+79991234567",
            "Мобильный телефон норм": None,
        })
        result = _collect_phone_set(row)
        
        self.assertEqual(len(result), 1)
        self.assertIn("+79991234567", result)
    
    def test_collect_phone_set_multiple(self):
        """Тестирует несколько телефонов."""
        row = pd.Series({
            "Рабочий телефон норм": "+79991234567",
            "Мобильный телефон норм": "+79991234568",
        })
        result = _collect_phone_set(row)
        
        self.assertEqual(len(result), 2)
    
    def test_collect_phone_set_empty(self):
        """Тестирует пустые значения."""
        row = pd.Series({
            "Рабочий телефон норм": None,
            "Мобильный телефон норм": None,
        })
        result = _collect_phone_set(row)
        
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
