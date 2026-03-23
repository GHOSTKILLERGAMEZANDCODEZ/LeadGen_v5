"""
Модульные тесты для modules/chart_generator.py
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.chart_generator import (
    build_leads_funnel,
    build_category_chart,
    build_manager_chart,
    build_refusals_chart,
    build_leads_source_chart,
)


class TestChartGenerator(unittest.TestCase):
    """Тесты для генератора графиков."""
    
    @patch('modules.chart_generator.plt.savefig')
    @patch('modules.chart_generator.plt.close')
    def test_build_leads_funnel_success(self, mock_close, mock_savefig):
        """Тестирует успешную воронку лидов."""
        leads_data = pd.DataFrame({
            'Категория': ['Категория 1', 'Категория 2', 'Категория 3'],
            'Количество': [100, 80, 60],
        })
        
        result = build_leads_funnel(leads_data, 'output.png')
        
        self.assertTrue(result)
        mock_savefig.assert_called_once()
        mock_close.assert_called()
    
    def test_build_leads_funnel_empty(self):
        """Тестирует пустые данные."""
        leads_data = pd.DataFrame()
        
        result = build_leads_funnel(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    def test_build_leads_funnel_no_columns(self):
        """Тестирует отсутствие колонок."""
        leads_data = pd.DataFrame({'other': [1, 2]})
        
        result = build_leads_funnel(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    @patch('modules.chart_generator.plt.savefig')
    @patch('modules.chart_generator.plt.close')
    def test_build_category_chart_success(self, mock_close, mock_savefig):
        """Тестирует успешную диаграмму категорий."""
        leads_data = pd.DataFrame({
            'Категория': ['A', 'B', 'C'],
            'Количество': [10, 20, 30],
        })
        
        result = build_category_chart(leads_data, 'output.png')
        
        self.assertTrue(result)
    
    def test_build_category_chart_empty(self):
        """Тестирует пустые данные."""
        leads_data = pd.DataFrame()
        
        result = build_category_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    def test_build_category_chart_no_columns(self):
        """Тестирует отсутствие колонок."""
        leads_data = pd.DataFrame({'other': [1, 2]})
        
        result = build_category_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    @patch('modules.chart_generator.plt.savefig')
    @patch('modules.chart_generator.plt.close')
    def test_build_manager_chart_success(self, mock_close, mock_savefig):
        """Тестирует успешную диаграмму менеджеров."""
        leads_data = pd.DataFrame({
            'Менеджер': ['Менеджер 1', 'Менеджер 2'],
            'Количество': [15, 25],
        })
        
        result = build_manager_chart(leads_data, 'output.png')
        
        self.assertTrue(result)
    
    def test_build_manager_chart_empty(self):
        """Тестирует пустые данные."""
        leads_data = pd.DataFrame()
        
        result = build_manager_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    def test_build_manager_chart_no_columns(self):
        """Тестирует отсутствие колонок."""
        leads_data = pd.DataFrame({'other': [1, 2]})
        
        result = build_manager_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    @patch('modules.chart_generator.plt.savefig')
    @patch('modules.chart_generator.plt.close')
    def test_build_refusals_chart_success(self, mock_close, mock_savefig):
        """Тестирует успешную диаграмму отказов."""
        leads_data = pd.DataFrame({
            'Причина отказа': ['Причина 1', 'Причина 2'],
            'Количество': [5, 10],
        })
        
        result = build_refusals_chart(leads_data, 'output.png')
        
        self.assertTrue(result)
    
    def test_build_refusals_chart_empty(self):
        """Тестирует пустые данные."""
        leads_data = pd.DataFrame()
        
        result = build_refusals_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    def test_build_refusals_chart_no_columns(self):
        """Тестирует отсутствие колонок."""
        leads_data = pd.DataFrame({'other': [1, 2]})
        
        result = build_refusals_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    @patch('modules.chart_generator.plt.savefig')
    @patch('modules.chart_generator.plt.close')
    def test_build_leads_source_chart_success(self, mock_close, mock_savefig):
        """Тестирует успешную диаграмму источников."""
        leads_data = pd.DataFrame({
            'Источник': ['Источник 1', 'Источник 2'],
            'Количество': [30, 40],
        })
        
        result = build_leads_source_chart(leads_data, 'output.png')
        
        self.assertTrue(result)
    
    def test_build_leads_source_chart_empty(self):
        """Тестирует пустые данные."""
        leads_data = pd.DataFrame()
        
        result = build_leads_source_chart(leads_data, 'output.png')
        
        self.assertFalse(result)
    
    def test_build_leads_source_chart_no_columns(self):
        """Тестирует отсутствие колонок."""
        leads_data = pd.DataFrame({'other': [1, 2]})
        
        result = build_leads_source_chart(leads_data, 'output.png')
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
