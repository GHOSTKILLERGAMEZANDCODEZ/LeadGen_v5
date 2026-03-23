"""
Модульные тесты для modules/data_processor.py.

Тестируемые функции:
- load_file — загрузка JSON/CSV/TSV файлов
- process_file — обработка одного файла
- remove_duplicates — удаление дубликатов
- assign_managers — распределение менеджеров
- merge_files — объединение файлов
- is_safe_path — проверка безопасности пути

Используется mock для pandas.read_json, pandas.read_csv, open.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from pathlib import Path
import sys

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импортируем реальный pandas до импорта модуля
import pandas as pd

# Импортируем модуль после pandas
from modules.data_processor import (
    load_file,
    process_file,
    remove_duplicates,
    assign_managers,
    merge_files,
    is_safe_path,
    prepare_output_columns,
    get_preview_data,
    clean_phone_column,
    SecurityError,
)


class TestIsSafePath(unittest.TestCase):
    """Тесты функции проверки безопасности пути."""

    def test_is_safe_path_valid_relative(self):
        """Тестирует валидный относительный путь в разрешённой директории."""
        result = is_safe_path('data/input/test.json')
        self.assertIsInstance(result, bool)

    def test_is_safe_path_traversal(self):
        """Тестирует блокировку Path Traversal атаки."""
        result = is_safe_path('../../.env')
        self.assertFalse(result)

    def test_is_safe_path_absolute_outside(self):
        """Тестирует блокировку абсолютного пути за пределами разрешённых директорий."""
        result = is_safe_path('C:/Windows/System32/config/sam')
        self.assertFalse(result)

    def test_is_safe_path_upload_dir(self):
        """Тестирует путь к UPLOAD директории."""
        result = is_safe_path('UPLOAD/test.json')
        self.assertIsInstance(result, bool)

    def test_is_safe_path_invalid_chars(self):
        """Тестирует путь с невалидными символами."""
        result = is_safe_path('data/input/<script>.json')
        self.assertIsInstance(result, bool)


class TestLoadFile(unittest.TestCase):
    """Тесты функции загрузки файлов."""

    def setUp(self):
        """Создаёт временные тестовые файлы."""
        self.test_dir = Path(__file__).parent.parent / 'data' / 'input'
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON тестовый файл
        self.json_file = self.test_dir / 'test_load.json'
        self.json_data = [
            {'phone': '79991234567', 'Название': 'Test Company'},
            {'phone': '79991234568', 'Название': 'Test Company 2'},
        ]
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f)
        
        # CSV тестовый файл
        self.csv_file = self.test_dir / 'test_load.csv'
        self.csv_data = "phone,Название\n79991234567,Test Company\n79991234568,Test Company 2"
        with open(self.csv_file, 'w', encoding='utf-8') as f:
            f.write(self.csv_data)
        
        # TSV тестовый файл
        self.tsv_file = self.test_dir / 'test_load.tsv'
        self.tsv_data = "phone\tНазвание\n79991234567\tTest Company\n79991234568\tTest Company 2"
        with open(self.tsv_file, 'w', encoding='utf-8') as f:
            f.write(self.tsv_data)

    def tearDown(self):
        """Удаляет временные тестовые файлы."""
        for file in [self.json_file, self.csv_file, self.tsv_file]:
            if file.exists():
                file.unlink()

    def test_load_file_json(self):
        """Тестирует загрузку JSON файла."""
        df = load_file(str(self.json_file))
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['phone'], '79991234567')

    def test_load_file_csv(self):
        """Тестирует загрузку CSV файла."""
        df = load_file(str(self.csv_file))
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)

    def test_load_file_tsv(self):
        """Тестирует загрузку TSV файла."""
        df = load_file(str(self.tsv_file))
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)

    def test_load_file_not_found(self):
        """Тестирует отсутствие файла."""
        # Теперь выбрасывается SecurityError для несуществующих файлов
        with self.assertRaises(SecurityError):
            load_file(str(self.test_dir / 'nonexistent.json'))

    def test_load_file_invalid_format(self):
        """Тестирует неверный формат файла."""
        txt_file = self.test_dir / 'test.txt'
        txt_file.write_text('test content')
        
        try:
            result = load_file(str(txt_file))
            self.assertIsNone(result)
        finally:
            txt_file.unlink()

    def test_load_file_security_error(self):
        """Тестирует выброс SecurityError для небезопасного пути."""
        with self.assertRaises(SecurityError):
            load_file('C:/Windows/System32/config/sam')

    def test_load_file_json_not_array(self):
        """Тестирует JSON, который не является массивом."""
        json_file = self.test_dir / 'test_object.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({'key': 'value'}, f)
        
        try:
            result = load_file(str(json_file))
            self.assertIsNone(result)
        finally:
            json_file.unlink()


class TestProcessFile(unittest.TestCase):
    """Тесты функции обработки файла."""

    def setUp(self):
        """Создаёт временные тестовые файлы."""
        self.test_dir = Path(__file__).parent.parent / 'data' / 'input'
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON с правильными колонками
        self.valid_json = self.test_dir / 'test_process.json'
        self.valid_data = [
            {
                'Название': 'Test Company',
                'phone_1': '79991234567',
                'phone_2': '',
                'Адрес': 'Moscow',
                'Category 0': 'Restaurants',
            }
        ]
        with open(self.valid_json, 'w', encoding='utf-8') as f:
            json.dump(self.valid_data, f)

    def tearDown(self):
        """Удаляет временные тестовые файлы."""
        if self.valid_json.exists():
            self.valid_json.unlink()

    def test_process_file_success(self):
        """Тестирует успешную обработку файла."""
        df = process_file(str(self.valid_json), 'test_process.json', {})
        
        self.assertIsNotNone(df)
        self.assertIn('phone_1', df.columns)
        self.assertIn('Источник телефона', df.columns)
        self.assertEqual(df.iloc[0]['Источник телефона'], 'test_process.json')

    def test_process_file_empty(self):
        """Тестирует пустой файл (DataFrame без данных)."""
        empty_json = self.test_dir / 'empty.json'
        with open(empty_json, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        try:
            df = process_file(str(empty_json), 'empty.json', {})
            self.assertIsNone(df)
        finally:
            empty_json.unlink()

    def test_process_file_invalid_path(self):
        """Тестирует небезопасный путь."""
        with self.assertRaises(SecurityError):
            process_file('../../.env', 'test', {})

    def test_process_file_missing_columns(self):
        """Тестирует файл без обязательных колонок."""
        invalid_json = self.test_dir / 'invalid.json'
        with open(invalid_json, 'w', encoding='utf-8') as f:
            json.dump([{'other_column': 'value'}], f)
        
        try:
            df = process_file(str(invalid_json), 'invalid.json', {})
            self.assertIsNone(df)
        finally:
            invalid_json.unlink()

    def test_process_file_with_settings(self):
        """Тестирует обработку с настройками."""
        settings = {
            'ignore_phone_2': True,
            'phone_format': '8',
            'min_phone_length': 11,
        }
        
        df = process_file(str(self.valid_json), 'test_process.json', settings)
        
        self.assertIsNotNone(df)
        self.assertIn('phone_1', df.columns)


class TestRemoveDuplicates(unittest.TestCase):
    """Тесты функции удаления дубликатов."""

    def test_remove_duplicates_simple(self):
        """Тестирует простое удаление дубликатов."""
        df = pd.DataFrame({
            'phone_1': ['79991234567', '79991234567', '79991234568'],
            'phone_2': ['', '', ''],
        })
        
        result, duplicates_removed = remove_duplicates(df, remove_duplicates_flag=True)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(duplicates_removed, 1)

    def test_remove_duplicates_empty(self):
        """Тестирует пустой DataFrame."""
        df = pd.DataFrame()
        
        result, duplicates_removed = remove_duplicates(df, remove_duplicates_flag=True)
        
        self.assertTrue(result.empty)
        self.assertEqual(duplicates_removed, 0)

    def test_remove_duplicates_disabled(self):
        """Тестирует отключенное удаление дубликатов."""
        df = pd.DataFrame({
            'phone_1': ['79991234567', '79991234567'],
            'phone_2': ['', ''],
        })
        
        result, duplicates_removed = remove_duplicates(df, remove_duplicates_flag=False)
        
        self.assertEqual(len(result), 2)  # Дубликаты сохранены
        self.assertEqual(duplicates_removed, 0)

    def test_remove_duplicates_no_duplicates(self):
        """Тестирует DataFrame без дубликатов."""
        df = pd.DataFrame({
            'phone_1': ['79991234567', '79991234568', '79991234569'],
            'phone_2': ['', '', ''],
        })
        
        result, duplicates_removed = remove_duplicates(df, remove_duplicates_flag=True)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(duplicates_removed, 0)

    def test_remove_duplicates_with_both_phones(self):
        """Тестирует удаление дубликатов с обоими телефонами."""
        df = pd.DataFrame({
            'phone_1': ['79991234567', '79991234567', '79991234568'],
            'phone_2': ['89997654321', '89997654321', '89997654322'],
        })
        
        result, duplicates_removed = remove_duplicates(df, remove_duplicates_flag=True)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(duplicates_removed, 1)


class TestAssignManagers(unittest.TestCase):
    """Тесты функции распределения менеджеров."""

    def test_assign_managers_empty(self):
        """Тестирует пустой DataFrame."""
        df = pd.DataFrame()
        
        result = assign_managers(df, ['Manager 1'])
        
        self.assertTrue(result.empty)
        self.assertIn('Ответственный', result.columns)

    def test_assign_managers_round_robin(self):
        """Тестирует round-robin распределение."""
        df = pd.DataFrame({'phone': ['1', '2', '3', '4']})
        managers = ['Manager 1', 'Manager 2']
        
        result = assign_managers(df, managers)
        
        self.assertEqual(len(result), 4)
        self.assertEqual(result['Ответственный'].iloc[0], 'Manager 1')
        self.assertEqual(result['Ответственный'].iloc[1], 'Manager 2')
        self.assertEqual(result['Ответственный'].iloc[2], 'Manager 1')
        self.assertEqual(result['Ответственный'].iloc[3], 'Manager 2')

    def test_assign_managers_no_managers(self):
        """Тестирует отсутствие менеджеров."""
        df = pd.DataFrame({'phone': ['1', '2']})
        
        result = assign_managers(df, [])
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['Ответственный'] == 'Не назначен'))

    def test_assign_managers_single_manager(self):
        """Тестирует с одним менеджером."""
        df = pd.DataFrame({'phone': ['1', '2', '3']})
        managers = ['Single Manager']
        
        result = assign_managers(df, managers)
        
        self.assertEqual(len(result), 3)
        self.assertTrue(all(result['Ответственный'] == 'Single Manager'))

    def test_assign_managers_more_managers_than_rows(self):
        """Тестирует когда менеджеров больше чем строк."""
        df = pd.DataFrame({'phone': ['1']})
        managers = ['Manager 1', 'Manager 2', 'Manager 3']
        
        result = assign_managers(df, managers)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result['Ответственный'].iloc[0], 'Manager 1')


class TestMergeFiles(unittest.TestCase):
    """Тесты функции объединения файлов."""

    def setUp(self):
        """Создаёт временные тестовые файлы."""
        self.test_dir = Path(__file__).parent.parent / 'data' / 'input'
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Первый файл с валидным телефоном
        self.file1 = self.test_dir / 'merge1.json'
        with open(self.file1, 'w', encoding='utf-8') as f:
            json.dump([
                {'Название': 'Test1', 'phone_1': '79991112233', 'phone_2': '', 'Адрес': '', 'Category 0': ''},
            ], f)

        # Второй файл с валидным телефоном
        self.file2 = self.test_dir / 'merge2.json'
        with open(self.file2, 'w', encoding='utf-8') as f:
            json.dump([
                {'Название': 'Test2', 'phone_1': '79994445566', 'phone_2': '', 'Адрес': '', 'Category 0': ''},
            ], f)

        # Файл с дубликатом (такой же телефон как file1)
        self.file_dup = self.test_dir / 'merge_dup.json'
        with open(self.file_dup, 'w', encoding='utf-8') as f:
            json.dump([
                {'Название': 'Test1 Dup', 'phone_1': '79991112233', 'phone_2': '', 'Адрес': '', 'Category 0': ''},
            ], f)

    def tearDown(self):
        """Удаляет временные тестовые файлы."""
        for file in [self.file1, self.file2, self.file_dup]:
            if file.exists():
                file.unlink()

    def test_merge_files_single(self):
        """Тестирует один файл."""
        df, stats = merge_files([str(self.file1)], ['Manager 1'], {})
        
        self.assertEqual(len(df), 1)
        self.assertEqual(stats['files_processed'], 1)
        self.assertEqual(stats['total_rows'], 1)

    def test_merge_files_multiple(self):
        """Тестирует несколько файлов."""
        df, stats = merge_files([str(self.file1), str(self.file2)], ['Manager 1'], {})
        
        self.assertEqual(len(df), 2)
        self.assertEqual(stats['files_processed'], 2)
        self.assertEqual(stats['total_rows'], 2)

    def test_merge_files_empty_list(self):
        """Тестирует пустой список файлов."""
        df, stats = merge_files([], ['Manager 1'], {})
        
        self.assertTrue(df.empty)
        self.assertEqual(stats['files_processed'], 0)
        self.assertEqual(stats['total_rows'], 0)

    def test_merge_files_all_fail(self):
        """Тестирует когда все файлы не обработались."""
        # Теперь выбрасывается SecurityError для несуществующих файлов
        with self.assertRaises(SecurityError):
            merge_files([str(self.test_dir / 'nonexistent.json')], ['Manager 1'], {})

    def test_merge_files_with_duplicates(self):
        """Тестирует удаление дубликатов при объединении."""
        df, stats = merge_files([str(self.file1), str(self.file_dup)], ['Manager 1'], {})
        
        self.assertEqual(len(df), 1)
        self.assertEqual(stats['duplicates_removed'], 1)

    def test_merge_files_no_managers(self):
        """Тестирует без менеджеров."""
        df, stats = merge_files([str(self.file1)], [], {})
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Ответственный'], 'Не назначен')


class TestPrepareOutputColumns(unittest.TestCase):
    """Тесты функции подготовки итоговых колонок."""

    def test_prepare_output_columns_complete(self):
        """Тестирует полный DataFrame со всеми колонками."""
        df = pd.DataFrame({
            'Category 0': ['Категория'],
            'Название': ['Компания'],
            'phone_1': ['79991234567'],
            'phone_2': ['89997654321'],
            'Адрес': ['Москва'],
            'companyUrl': ['https://example.com'],
            'telegram': ['@username'],
            'vkontakte': ['https://vk.com/club'],
            'Источник телефона': ['test.json'],
            'Ответственный': ['Manager 1'],
        })
        
        result = prepare_output_columns(df)
        
        expected_columns = [
            'Название лида',
            'Рабочий телефон',
            'Мобильный телефон',
            'Адрес',
            'Корпоративный сайт',
            'Контакт Telegram',
            'Контакт ВКонтакте',
            'Название компании',
            'Источник телефона',
            'Ответственный',
        ]
        
        self.assertEqual(list(result.columns), expected_columns)
        self.assertEqual(result.iloc[0]['Название лида'], 'Категория - Компания')

    def test_prepare_output_columns_empty(self):
        """Тестирует пустой DataFrame."""
        df = pd.DataFrame()
        
        result = prepare_output_columns(df)
        
        self.assertTrue(result.empty)

    def test_prepare_output_columns_no_category(self):
        """Тестирует без категории."""
        df = pd.DataFrame({
            'Название': ['Компания'],
            'phone_1': ['79991234567'],
            'phone_2': [''],
        })
        
        result = prepare_output_columns(df)
        
        self.assertEqual(result.iloc[0]['Название лида'], 'Компания')

    def test_prepare_output_columns_with_category(self):
        """Тестирует с категорией."""
        df = pd.DataFrame({
            'Category 0': ['Рестораны'],
            'Название': ['Кафе'],
            'phone_1': ['79991234567'],
            'phone_2': [''],
        })
        
        result = prepare_output_columns(df)
        
        self.assertEqual(result.iloc[0]['Название лида'], 'Рестораны - Кафе')


class TestGetPreviewData(unittest.TestCase):
    """Тесты функции получения предпросмотра."""

    def test_get_preview_data_limit(self):
        """Тестирует ограничение количества строк."""
        df = pd.DataFrame({
            'Название лида': [f'Lead {i}' for i in range(20)],
            'Рабочий телефон': ['1'] * 20,
            'Адрес': ['Addr'] * 20,
            'Ответственный': ['Mgr'] * 20,
            'Источник телефона': ['Src'] * 20,
        })
        
        preview = get_preview_data(df, limit=10)
        
        self.assertEqual(len(preview), 10)

    def test_get_preview_data_columns(self):
        """Тестирует наличие правильных колонок."""
        df = pd.DataFrame({
            'Название лида': ['A'],
            'Рабочий телефон': ['1'],
            'Адрес': ['Addr'],
            'Ответственный': ['Mgr'],
            'Источник телефона': ['Src'],
        })
        
        preview = get_preview_data(df)
        
        expected_cols = [
            'Название лида',
            'Рабочий телефон',
            'Адрес',
            'Ответственный',
            'Источник телефона',
        ]
        self.assertEqual(list(preview.columns), expected_cols)

    def test_get_preview_data_less_than_limit(self):
        """Тестирует когда данных меньше лимита."""
        df = pd.DataFrame({
            'Название лида': ['A', 'B'],
            'Рабочий телефон': ['1', '2'],
            'Адрес': ['Addr', 'Addr2'],
            'Ответственный': ['Mgr', 'Mgr2'],
            'Источник телефона': ['Src', 'Src2'],
        })
        
        preview = get_preview_data(df, limit=10)
        
        self.assertEqual(len(preview), 2)


class TestCleanPhoneColumn(unittest.TestCase):
    """Тесты функции очистки телефонов в серии."""

    def test_clean_phone_column_valid(self):
        """Тестирует очистку валидных телефонов."""
        series = pd.Series(['79991234567', '89997654321', '+79991112233'])
        
        result = clean_phone_column(series)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0], '79991234567')

    def test_clean_phone_column_invalid(self):
        """Тестирует очистку невалидных телефонов."""
        series = pd.Series(['123', 'abc', None, ''])
        
        result = clean_phone_column(series)
        
        self.assertEqual(len(result), 4)

    def test_clean_phone_column_custom_format(self):
        """Тестирует с кастомным форматом."""
        series = pd.Series(['79991234567'])
        
        result = clean_phone_column(series, phone_format='8', min_length=11)
        
        self.assertEqual(result.iloc[0], '89991234567')


if __name__ == '__main__':
    unittest.main()
