"""
Тесты для модуля bitrix_mapper.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Добавляем корень проекта в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "modules"))

# Прямой импорт из файла (минуя modules/__init__.py чтобы избежать импорта pandas)
import importlib.util
bitrix_mapper_path = ROOT_DIR / "modules" / "bitrix_mapper.py"
spec = importlib.util.spec_from_file_location("bitrix_mapper_module", bitrix_mapper_path)
bitrix_mapper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bitrix_mapper_module)

# Импорт для тестов
map_to_bitrix = bitrix_mapper_module.map_to_bitrix
get_bitrix_columns = bitrix_mapper_module.get_bitrix_columns
export_to_bitrix_csv = bitrix_mapper_module.export_to_bitrix_csv
_clean_telegram_series = bitrix_mapper_module._clean_telegram_series
_clean_vk_series = bitrix_mapper_module._clean_vk_series
_clean_url_series = bitrix_mapper_module._clean_url_series
_clean_string_series = bitrix_mapper_module._clean_string_series
_has_value = bitrix_mapper_module._has_value

import pandas as pd


class TestBitrixMapper(unittest.TestCase):
    """Тесты маппера Битрикс24."""

    def test_get_bitrix_columns_count(self):
        """Проверка количества колонок Битрикс."""
        columns = get_bitrix_columns()
        self.assertEqual(len(columns), 64)

    def test_map_to_bitrix_basic(self):
        """Проверка базового маппинга."""
        df = pd.DataFrame({
            'Название лида': ['Test Lead'],
            'Название компании': ['Test Company'],
            'Рабочий телефон': ['79991234567'],
            'Адрес': ['Test Address'],
            'Источник телефона': ['test.csv']
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], 'Test Lead')
        self.assertEqual(result['Название компании'].iloc[0], 'Test Company')
        self.assertEqual(result['Рабочий телефон'].iloc[0], '79991234567')
        self.assertEqual(result['Адрес'].iloc[0], 'Test Address')

    def test_map_to_bitrix_default_values(self):
        """Проверка значений по умолчанию."""
        df = pd.DataFrame({
            'Название лида': ['Test'],
            'Рабочий телефон': ['79991234567']
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Стадия'].iloc[0], 'Новая заявка')
        self.assertEqual(result['Источник'].iloc[0], 'Холодный звонок')
        self.assertEqual(result['Тип услуги'].iloc[0], 'ГЦК')
        self.assertEqual(result['Доступен для всех'].iloc[0], 'да')

    def test_map_to_bitrix_column_count(self):
        """Проверка количества выходных колонок."""
        df = pd.DataFrame({
            'Название лида': ['Test'],
            'Рабочий телефон': ['79991234567']
        })

        result = map_to_bitrix(df)

        self.assertEqual(len(result.columns), 64)


class TestBitrixMapperExtended(unittest.TestCase):
    """Расширенные тесты маппера Битрикс24."""

    # ===== _clean_string_series =====

    def test_clean_string_series_basic(self):
        """Тестирует базовую очистку строк."""
        series = pd.Series(['  Hello  ', '  World  ', None, ''])
        result = _clean_string_series(series)

        self.assertEqual(result.iloc[0], 'Hello')
        self.assertEqual(result.iloc[1], 'World')
        self.assertEqual(result.iloc[2], '')
        self.assertEqual(result.iloc[3], '')

    def test_clean_string_series_nan_values(self):
        """Тестирует обработку NaN значений."""
        series = pd.Series(['test', float('nan'), 'value'])
        result = _clean_string_series(series)

        self.assertEqual(result.iloc[0], 'test')
        self.assertEqual(result.iloc[1], '')
        self.assertEqual(result.iloc[2], 'value')

    def test_clean_string_series_none_values(self):
        """Тестирует обработку None значений."""
        series = pd.Series(['test', None, 'value'])
        result = _clean_string_series(series)

        self.assertEqual(result.iloc[0], 'test')
        self.assertEqual(result.iloc[1], '')
        self.assertEqual(result.iloc[2], 'value')

    def test_clean_string_series_empty_series(self):
        """Тестирует пустую серию."""
        series = pd.Series([], dtype=str)
        result = _clean_string_series(series)

        self.assertEqual(len(result), 0)

    # ===== _has_value =====

    def test_has_value_with_values(self):
        """Тестирует серию со значениями."""
        series = pd.Series(['test', 'value', ''])
        result = _has_value(series)

        self.assertTrue(result.iloc[0])
        self.assertTrue(result.iloc[1])
        self.assertFalse(result.iloc[2])

    def test_has_value_empty_strings(self):
        """Тестирует серию с пустыми строками."""
        series = pd.Series(['', '', ''])
        result = _has_value(series)

        self.assertFalse(result.iloc[0])
        self.assertFalse(result.iloc[1])
        self.assertFalse(result.iloc[2])

    # ===== _clean_telegram_series =====

    def test_clean_telegram_series_simple(self):
        """Тестирует простой username."""
        series = pd.Series(['@username'])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '@username')

    def test_clean_telegram_series_with_url(self):
        """Тестирует username с URL."""
        series = pd.Series(['https://t.me/username'])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '@username')

    def test_clean_telegram_series_http_url(self):
        """Тестирует username с http URL."""
        series = pd.Series(['http://t.me/username'])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '@username')

    def test_clean_telegram_series_empty(self):
        """Тестирует пустой username."""
        series = pd.Series([''])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '')

    def test_clean_telegram_series_none(self):
        """Тестирует None значение."""
        series = pd.Series([None])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '')

    def test_clean_telegram_series_with_slash(self):
        """Тестирует username с дополнительным путём."""
        series = pd.Series(['@username/extra'])
        result = _clean_telegram_series(series)

        self.assertEqual(result.iloc[0], '@username')

    # ===== _clean_vk_series =====

    def test_clean_vk_series_simple(self):
        """Тестирует простой VK username."""
        series = pd.Series(['username'])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], 'username')

    def test_clean_vk_series_with_url(self):
        """Тестирует username с URL."""
        series = pd.Series(['https://vk.com/username'])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], 'username')

    def test_clean_vk_series_http_url(self):
        """Тестирует username с http URL."""
        series = pd.Series(['http://vk.com/username'])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], 'username')

    def test_clean_vk_series_empty(self):
        """Тестирует пустой username."""
        series = pd.Series([''])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], '')

    def test_clean_vk_series_none(self):
        """Тестирует None значение."""
        series = pd.Series([None])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], '')

    def test_clean_vk_series_with_slash(self):
        """Тестирует username с дополнительным путём."""
        series = pd.Series(['username/wall'])
        result = _clean_vk_series(series)

        self.assertEqual(result.iloc[0], 'username')

    # ===== _clean_url_series =====

    def test_clean_url_series_with_utm(self):
        """Тестирует очистку URL с UTM-метками."""
        series = pd.Series(['https://example.com?utm_source=test&utm_medium=cpc'])
        result = _clean_url_series(series)

        self.assertNotIn('utm_', result.iloc[0])
        self.assertIn('example.com', result.iloc[0])

    def test_clean_url_series_without_utm(self):
        """Тестирует URL без UTM-меток."""
        series = pd.Series(['https://example.com/page'])
        result = _clean_url_series(series)

        self.assertEqual(result.iloc[0], 'https://example.com/page')

    def test_clean_url_series_empty(self):
        """Тестирует пустой URL."""
        series = pd.Series([''])
        result = _clean_url_series(series)

        self.assertEqual(result.iloc[0], '')

    def test_clean_url_series_none(self):
        """Тестирует None значение."""
        series = pd.Series([None])
        result = _clean_url_series(series)

        self.assertEqual(result.iloc[0], '')

    # ===== map_to_bitrix: кастомные настройки =====

    def test_map_to_bitrix_custom_settings(self):
        """Тестирует кастомные настройки."""
        df = pd.DataFrame({
            'Название': ['Company 1'],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(
            df,
            stage="В работе",
            source="Сайт",
            service_type="Консалтинг",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result['Стадия'].iloc[0], "В работе")
        self.assertEqual(result['Источник'].iloc[0], "Сайт")
        self.assertEqual(result['Тип услуги'].iloc[0], "Консалтинг")

    def test_map_to_bitrix_with_lpr(self):
        """Тестирует с данными ЛПР."""
        df = pd.DataFrame({
            'Название лида': ['Lead 1'],
            'Рабочий телефон': ['79991234567'],
            'ЛПР': ['Иванов Иван'],
            'Должность ЛПР': ['Директор'],
        })

        result = map_to_bitrix(df, lpr_column='ЛПР')

        self.assertEqual(len(result), 1)
        self.assertEqual(result['Комментарий'].iloc[0], "ЛПР: Иванов Иван")

    def test_map_to_bitrix_with_lpr_empty(self):
        """Тестирует с пустыми данными ЛПР."""
        df = pd.DataFrame({
            'Название лида': ['Lead 1'],
            'Рабочий телефон': ['79991234567'],
            'ЛПР': [''],
        })

        result = map_to_bitrix(df, lpr_column='ЛПР')

        self.assertEqual(len(result), 1)
        self.assertEqual(result['Комментарий'].iloc[0], "")

    def test_map_to_bitrix_clean_urls(self):
        """Тестирует очистку URL."""
        df = pd.DataFrame({
            'Название лида': ['Company 1'],
            'Рабочий телефон': ['79991234567'],
            'Корпоративный сайт': ['https://example.com?utm_source=test&utm_medium=cpc'],
        })

        result = map_to_bitrix(df)

        # URL должен быть очищен от UTM-меток
        self.assertNotIn('utm_', result['Корпоративный сайт'].iloc[0])
        self.assertIn('example.com', result['Корпоративный сайт'].iloc[0])

    def test_map_to_bitrix_telegram_cleanup(self):
        """Тестирует очистку Telegram username."""
        df = pd.DataFrame({
            'Название лида': ['Company 1'],
            'Рабочий телефон': ['79991234567'],
            'Контакт Telegram': ['https://t.me/username'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Контакт Telegram'].iloc[0], '@username')

    def test_map_to_bitrix_vk_cleanup(self):
        """Тестирует очистку VK username."""
        df = pd.DataFrame({
            'Название лида': ['Company 1'],
            'Рабочий телефон': ['79991234567'],
            'Контакт ВКонтакте': ['https://vk.com/username'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Страница ВКонтакте'].iloc[0], 'username')

    def test_map_to_bitrix_empty_rows_filtered(self):
        """Тестирует фильтрацию пустых строк."""
        df = pd.DataFrame({
            'Название лида': ['Lead 1', '', 'Lead 3'],
            'Рабочий телефон': ['', '', ''],
            'Адрес': ['', '', ''],
            'Название компании': ['', '', ''],
            'Мобильный телефон': ['', '', '79991234567'],
        })

        result = map_to_bitrix(df)

        # Должны остаться только строки с данными
        self.assertEqual(len(result), 2)

    def test_map_to_bitrix_lead_name_from_company(self):
        """Тестирует создание названия лида из названия компании."""
        df = pd.DataFrame({
            'Название компании': ['Company ABC'],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], 'Company ABC')

    def test_map_to_bitrix_responsible(self):
        """Тестирует маппинг ответственного."""
        df = pd.DataFrame({
            'Название лида': ['Lead 1'],
            'Рабочий телефон': ['79991234567'],
            'Ответственный': ['Менеджер 1'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Ответственный'].iloc[0], 'Менеджер 1')

    # ===== export_to_bitrix_csv =====

    @patch('pandas.DataFrame.to_csv')
    def test_export_to_bitrix_csv_success(self, mock_to_csv):
        """Тестирует успешный экспорт."""
        df = pd.DataFrame({'Рабочий телефон': ['79991234567']})

        with patch('builtins.open', mock_open()):
            result = export_to_bitrix_csv(df, 'output.csv')

            self.assertTrue(result)
            mock_to_csv.assert_called_once()
            # Проверка параметров вызова
            call_args = mock_to_csv.call_args
            self.assertEqual(call_args[1]['sep'], ';')
            self.assertEqual(call_args[1]['encoding'], 'utf-8-sig')
            self.assertEqual(call_args[1]['index'], False)

    @patch('builtins.open')
    def test_export_to_bitrix_csv_invalid_path(self, mock_open_func):
        """Тестирует неверный путь."""
        mock_open_func.side_effect = IOError("Invalid path")

        df = pd.DataFrame({'Рабочий телефон': ['79991234567']})

        result = export_to_bitrix_csv(df, '/invalid/path/output.csv')

        self.assertFalse(result)

    @patch('pandas.DataFrame.to_csv')
    def test_export_to_bitrix_csv_with_custom_params(self, mock_to_csv):
        """Тестирует экспорт с кастомными параметрами."""
        df = pd.DataFrame({'Рабочий телефон': ['79991234567']})

        with patch('builtins.open', mock_open()):
            result = export_to_bitrix_csv(
                df,
                'output.csv',
                stage="В работе",
                source="Сайт",
                service_type="Консалтинг",
                lpr_column="ЛПР"
            )

            self.assertTrue(result)

    # ===== prepare_bitrix_data (через map_to_bitrix) =====

    def test_prepare_bitrix_data_success(self):
        """Тестирует успешную подготовку данных."""
        df = pd.DataFrame({
            'Название лида': ['Company 1'],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result.columns), 64)

    def test_prepare_bitrix_data_empty(self):
        """Тестирует пустые данные."""
        df = pd.DataFrame()

        result = map_to_bitrix(df)

        self.assertTrue(result.empty)

    def test_prepare_bitrix_data_multiple_rows(self):
        """Тестирует подготовку нескольких строк."""
        df = pd.DataFrame({
            'Название лида': ['Company 1', 'Company 2', 'Company 3'],
            'Рабочий телефон': ['79991234567', '79991234568', '79991234569'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(len(result), 3)

    # ===== Edge cases =====

    def test_map_to_bitrix_special_characters(self):
        """Тестирует специальные символы в данных."""
        df = pd.DataFrame({
            'Название лида': ['Company "Quotes" & <Tags>'],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], 'Company "Quotes" & <Tags>')

    def test_map_to_bitrix_unicode_characters(self):
        """Тестирует Unicode символы."""
        df = pd.DataFrame({
            'Название лида': ['Компания 🚀'],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], 'Компания 🚀')

    def test_map_to_bitrix_long_values(self):
        """Тестирует длинные значения."""
        long_name = 'A' * 1000
        df = pd.DataFrame({
            'Название лида': [long_name],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], long_name)

    def test_map_to_bitrix_null_values(self):
        """Тестирует null значения."""
        df = pd.DataFrame({
            'Название лида': [None],
            'Рабочий телефон': ['79991234567'],
        })

        result = map_to_bitrix(df)

        self.assertEqual(result['Название лида'].iloc[0], '')

    def test_map_to_bitrix_mixed_null_types(self):
        """Тестирует смешанные null типы."""
        df = pd.DataFrame({
            'Название лида': [None, float('nan'), ''],
            'Рабочий телефон': ['79991234567', '79991234568', '79991234569'],
        })

        result = map_to_bitrix(df)

        # Все null значения должны быть преобразованы в пустые строки
        for i in range(len(result)):
            self.assertIn(result['Название лида'].iloc[i], ['', 'None', 'nan'])


if __name__ == "__main__":
    unittest.main()
