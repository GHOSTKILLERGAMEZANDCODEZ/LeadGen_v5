"""
Тесты для модуля bitrix_analytics.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.bitrix_analytics import (
    extract_category,
    normalize_phone,
    calculate_metrics
)
import pandas as pd


class TestBitrixAnalytics(unittest.TestCase):
    """Тесты аналитики Битрикс24."""
    
    def test_extract_category_simple(self):
        """Проверка извлечения категории."""
        self.assertEqual(
            extract_category("Металлоконструкции - Уралсвармет"),
            "Металлоконструкции"
        )
    
    def test_extract_category_no_separator(self):
        """Проверка без разделителя."""
        self.assertEqual(
            extract_category("Просто название"),
            "Просто название"
        )
    
    def test_extract_category_empty(self):
        """Проверка пустого значения."""
        self.assertEqual(extract_category(""), "")
        self.assertEqual(extract_category(None), "")
    
    def test_normalize_phone_russian(self):
        """Проверка нормализации российских номеров."""
        self.assertEqual(normalize_phone("+79991234567"), "79991234567")
        self.assertEqual(normalize_phone("89991234567"), "79991234567")
        self.assertEqual(normalize_phone("79991234567"), "79991234567")
    
    def test_normalize_phone_formatted(self):
        """Проверка нормализации форматированных номеров."""
        self.assertEqual(normalize_phone("+7 (999) 123-45-67"), "79991234567")
        self.assertEqual(normalize_phone("8 (999) 123 45 67"), "79991234567")
    
    def test_normalize_phone_empty(self):
        """Проверка пустых значений."""
        self.assertIsNone(normalize_phone(""))
        self.assertIsNone(normalize_phone(None))
        self.assertIsNone(normalize_phone("123"))  # Слишком короткий
    
    def test_calculate_metrics_basic(self):
        """Проверка расчёта метрик."""
        # Создаём тестовые данные
        leads = pd.DataFrame({
            'ID': ['1', '2', '3'],
            'Название лида': ['Категория1 - Лид1', 'Категория2 - Лид2', 'Категория1 - Лид3'],
            'Стадия': ['Новая', 'В работе', 'Новая'],
            'Ответственный': ['Менеджер1', 'Менеджер2', 'Менеджер1'],
            'Источник телефона': ['file1.csv', 'file1.csv', 'file1.csv'],
            'Причина отказа': ['Недозвон', None, 'Неактуально'],
            'Наш лид': [True, True, True]
        })
        
        # Добавляем категорию
        leads['Категория'] = leads['Название лида'].apply(extract_category)
        
        deals = pd.DataFrame({
            'ID': ['1', '2'],
            'Название сделки': ['Категория1 - Лид1', 'Категория2 - Лид2'],
            'Стадия сделки': ['Новая', 'Успешно'],
            'Причина отказа': [None, 'Успешно реализовано'],
            'Наша сделка': [True, True],
            'Категория (из лида)': ['Категория1', 'Категория2'],
            'Менеджер (из лида)': ['Менеджер1', 'Менеджер2']
        })
        
        metrics = calculate_metrics(leads, deals)
        
        self.assertEqual(metrics['total_leads'], 3)
        self.assertEqual(metrics['total_deals'], 2)
        self.assertAlmostEqual(metrics['conversion_rate'], 66.67, places=1)


if __name__ == "__main__":
    unittest.main()
