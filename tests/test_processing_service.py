"""
Модульные тесты для ProcessingService.
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd
import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.services.processing_service import ProcessingService


class TestProcessingService(unittest.TestCase):
    """Тесты для ProcessingService."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.db_mock = MagicMock()
        self.config = {
            "processing": {
                "phone_format": "7",
                "remove_duplicates": True,
                "min_phone_length": 10,
            },
            "bitrix": {
                "stage": "Новая заявка",
                "source": "Холодный звонок",
            }
        }
        self.service = ProcessingService(self.db_mock, self.config)
    
    def test_init(self):
        """Тест инициализации сервиса."""
        db_mock = MagicMock()
        config = {"processing": {}, "bitrix": {}}
        service = ProcessingService(db_mock, config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service._db, db_mock)
        self.assertEqual(service._config, config)
    
    def test_validate_files_success(self):
        """Тест валидации существующих файлов."""
        # Создаём временные файлы
        test_files = []
        for i in range(2):
            test_file = Path(__file__).parent / f"test_file_{i}.json"
            test_file.write_text('{"test": "data"}')
            test_files.append(str(test_file))
        
        try:
            # Не должно выбрасывать исключений
            self.service._validate_files(test_files)
        finally:
            # Удаляем временные файлы
            for f in test_files:
                Path(f).unlink()
    
    def test_validate_files_not_found(self):
        """Тест валидации несуществующих файлов."""
        with self.assertRaises(FileNotFoundError):
            self.service._validate_files(["nonexistent_file.json"])
    
    def test_process_files_empty_managers(self):
        """Тест обработки с пустым списком менеджеров."""
        # Создаём временный файл для прохождения валидации
        test_file = Path(__file__).parent / "test_file.json"
        test_file.write_text('{"test": "data"}')
        
        try:
            with self.assertRaises(ValueError) as context:
                self.service.process_files([str(test_file)], [])
            
            self.assertIn("менеджеров не может быть пустым", str(context.exception))
        finally:
            # Удаляем временный файл
            test_file.unlink()
    
    @patch('modules.services.processing_service.merge_files')
    @patch('modules.services.processing_service.map_to_bitrix')
    def test_process_files_success(self, mock_map, mock_merge):
        """Тест успешной обработки файлов."""
        # Создаём моки для DataFrame
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.empty = False
        mock_merge.return_value = (mock_df, {"total_rows": 100, "duplicates_removed": 5})
        mock_map.return_value = mock_df
        
        file_paths = [str(Path(__file__).parent / "test.json")]
        managers = ["Manager 1", "Manager 2"]
        
        # Создаём файл для теста
        Path(file_paths[0]).write_text('{"test": "data"}')
        
        try:
            df_result, stats = self.service.process_files(file_paths, managers)
            
            # Проверяем результаты
            self.assertEqual(df_result, mock_df)
            self.assertIn("processing_time_ms", stats)
            self.assertEqual(stats["total_rows"], 100)
            
            # Проверяем вызовы
            mock_merge.assert_called_once()
            mock_map.assert_called_once()
            self.db_mock.add_processing_record.assert_called_once()
        finally:
            # Удаляем тестовый файл
            Path(file_paths[0]).unlink()
    
    def test_export_to_csv(self):
        """Тест экспорта в CSV."""
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        output_path = str(Path(__file__).parent / "test_output.csv")
        
        try:
            result_path = self.service.export_to_csv(df, output_path)
            
            self.assertEqual(result_path, output_path)
            self.assertTrue(Path(output_path).exists())
        finally:
            # Удаляем тестовый файл
            if Path(output_path).exists():
                Path(output_path).unlink()
    
    @patch('modules.services.processing_service.export_to_bitrix_csv')
    def test_export_to_csv_failure(self, mock_export):
        """Тест неудачного экспорта в CSV."""
        mock_export.return_value = False
        df = pd.DataFrame({"col1": [1, 2]})
        
        with self.assertRaises(IOError) as context:
            self.service.export_to_csv(df, "output.csv")
        
        self.assertIn("Не удалось экспортировать", str(context.exception))
    
    def test_save_to_database_error_handling(self):
        """Тест обработки ошибок при сохранении в БД."""
        # Настраиваем mock на выбрасывание исключения
        self.db_mock.add_processing_record.side_effect = Exception("DB Error")
        
        # Не должно выбрасывать исключение (ошибка логируется)
        self.service._save_to_database(["file.json"], {"total_rows": 10})
        
        # Проверяем что вызов был
        self.db_mock.add_processing_record.assert_called_once()


if __name__ == "__main__":
    unittest.main()
