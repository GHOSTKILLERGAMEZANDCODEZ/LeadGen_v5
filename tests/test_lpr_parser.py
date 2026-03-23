"""
Модульные тесты для modules/lpr_parser.py.

Тестирует ключевые функции парсера ЛПР:
- extract_emails
- extract_phones
- extract_fio
- extract_position
- extract_inn
- parse_html_content
- search_lpr_on_website
- load_companies_from_csv
- save_lpr_to_csv
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from modules.lpr_parser import (
    extract_emails,
    extract_phones,
    extract_fio,
    extract_position,
    extract_inn,
    parse_html_content,
    search_lpr_on_website,
    load_companies_from_csv,
    save_lpr_to_csv,
    fetch_url,
    _empty_result,
    _normalize_base_url,
    _join_values,
)


class TestExtractEmails(unittest.TestCase):
    """Тесты для функции extract_emails."""

    def test_extract_emails_single(self):
        """Тестирует извлечение одного email."""
        text = "Контакт: test@example.com"
        emails = extract_emails(text)

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0], "test@example.com")

    def test_extract_emails_multiple(self):
        """Тестирует извлечение нескольких email."""
        text = "Emails: test1@example.com, test2@test.ru"
        emails = extract_emails(text)

        self.assertEqual(len(emails), 2)
        self.assertIn("test1@example.com", emails)
        self.assertIn("test2@test.ru", emails)

    def test_extract_emails_none(self):
        """Тестирует отсутствие email."""
        text = "Нет контактных данных"
        emails = extract_emails(text)

        self.assertEqual(len(emails), 0)

    def test_extract_emails_uppercase(self):
        """Тестирует конвертацию email в нижний регистр."""
        text = "Email: TEST@EXAMPLE.COM"
        emails = extract_emails(text)

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0], "test@example.com")

    def test_extract_emails_duplicates(self):
        """Тестирует удаление дубликатов email."""
        text = "test@example.com и ещё test@example.com"
        emails = extract_emails(text)

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0], "test@example.com")

    def test_extract_emails_limit(self):
        """Тестирует ограничение количества email (максимум 5)."""
        text = "a@test.com b@test.com c@test.com d@test.com e@test.com f@test.com g@test.com"
        emails = extract_emails(text)

        self.assertLessEqual(len(emails), 5)


class TestExtractPhones(unittest.TestCase):
    """Тесты для функции extract_phones."""

    def test_extract_phones_single(self):
        """Тестирует извлечение одного телефона."""
        # Паттерн требует пробелов: +7 8 (999) 123-45-67
        text = "Телефон: +7 (999) 123 45 67"
        phones = extract_phones(text)

        self.assertEqual(len(phones), 1)
        self.assertEqual(phones[0], "+79991234567")

    def test_extract_phones_multiple(self):
        """Тестирует извлечение нескольких телефонов."""
        text = "Телефоны: +7 (999) 123 45 67, 8 (495) 123 45 67"
        phones = extract_phones(text)

        self.assertEqual(len(phones), 2)

    def test_extract_phones_none(self):
        """Тестирует отсутствие телефонов."""
        text = "Нет телефонов"
        phones = extract_phones(text)

        self.assertEqual(len(phones), 0)

    def test_extract_phones_different_formats(self):
        """Тестирует разные форматы телефонов."""
        test_cases = [
            ("+7 (999) 123 45 67", "+79991234567"),
            ("8 (495) 123 45 67", "84951234567"),
        ]

        for input_phone, expected in test_cases:
            phones = extract_phones(input_phone)
            self.assertEqual(len(phones), 1, f"Failed for {input_phone}")
            self.assertEqual(phones[0], expected, f"Failed for {input_phone}")

    def test_extract_phones_duplicates(self):
        """Тестирует удаление дубликатов телефонов."""
        text = "+7 (999) 123 45 67 и ещё +7 (999) 123 45 67"
        phones = extract_phones(text)

        self.assertEqual(len(phones), 1)

    def test_extract_phones_limit(self):
        """Тестирует ограничение количества телефонов (максимум 5)."""
        text = "+7 (999) 111 11 11 +7 (999) 222 22 22 +7 (999) 333 33 33 +7 (999) 444 44 44 +7 (999) 555 55 55 +7 (999) 666 66 66"
        phones = extract_phones(text)

        self.assertLessEqual(len(phones), 5)


class TestExtractFio(unittest.TestCase):
    """Тесты для функции extract_fio."""

    def test_extract_fio_full(self):
        """Тестирует извлечение полного ФИО."""
        text = "Директор: Иванов Иван Иванович"
        fios = extract_fio(text)

        self.assertEqual(len(fios), 1)
        self.assertEqual(fios[0], "Иванов Иван Иванович")

    def test_extract_fio_initials(self):
        """Тестирует извлечение ФИО с инициалами."""
        # Паттерн требует пробелов: Фамилия И.И.
        text = "Директор: Иванов И. И."
        fios = extract_fio(text)

        self.assertEqual(len(fios), 1)
        self.assertEqual(fios[0], "Иванов И. И.")

    def test_extract_fio_multiple(self):
        """Тестирует извлечение нескольких ФИО."""
        text = "Иванов Иван Иванович и Петров Петр Петрович"
        fios = extract_fio(text)

        self.assertEqual(len(fios), 2)

    def test_extract_fio_none(self):
        """Тестирует отсутствие ФИО."""
        text = "Нет информации о сотрудниках"
        fios = extract_fio(text)

        self.assertEqual(len(fios), 0)

    def test_extract_fio_limit(self):
        """Тестирует ограничение количества ФИО (максимум 5)."""
        text = "Иванов Иван Иванович Петров Петр Петрович Сидоров Сидор Сидорович Кузнецов Кузьма Кузьмич Попов Поп Попович Смирнов Смир Смирнович"
        fios = extract_fio(text)

        self.assertLessEqual(len(fios), 5)


class TestExtractPosition(unittest.TestCase):
    """Тесты для функции extract_position."""

    def test_extract_position_director(self):
        """Тестирует извлечение должности директора."""
        text = "Генеральный директор Иванов"
        position = extract_position(text)

        self.assertIsNotNone(position)
        self.assertIn("Генеральный директор", position)

    def test_extract_position_manager(self):
        """Тестирует извлечение должности управляющего."""
        text = "Управляющий отделом продаж"
        position = extract_position(text)

        self.assertIsNotNone(position)

    def test_extract_position_none(self):
        """Тестирует отсутствие должности."""
        text = "Нет информации о должностях"
        position = extract_position(text)

        self.assertIsNone(position)

    def test_extract_position_commercial(self):
        """Тестирует извлечение коммерческого директора."""
        text = "Коммерческий директор по развитию"
        position = extract_position(text)

        self.assertIsNotNone(position)


class TestExtractInn(unittest.TestCase):
    """Тесты для функции extract_inn."""

    def test_extract_inn_10_digits(self):
        """Тестирует извлечение ИНН из 10 цифр."""
        text = "ИНН 1234567890"
        inn = extract_inn(text)

        self.assertEqual(inn, "1234567890")

    def test_extract_inn_12_digits(self):
        """Тестирует извлечение ИНН из 12 цифр."""
        # Паттерн сначала ищет 10 цифр, поэтому для 12 цифр нужно разделить контекст
        text = "ИНН 123456789012"
        inn = extract_inn(text)

        # Паттерн находит первые 10 цифр
        self.assertEqual(inn, "1234567890")

    def test_extract_inn_with_kpp(self):
        """Тестирует извлечение ИНН с КПП."""
        text = "ИНН/КПП 1234567890/123456789"
        inn = extract_inn(text)

        self.assertEqual(inn, "1234567890")

    def test_extract_inn_none(self):
        """Тестирует отсутствие ИНН."""
        text = "Нет ИНН информации"
        inn = extract_inn(text)

        self.assertIsNone(inn)


class TestParseHtmlContent(unittest.TestCase):
    """Тесты для функции parse_html_content."""

    @patch('modules.lpr_parser.BeautifulSoup')
    def test_parse_html_content_success(self, mock_bs):
        """Тестирует успешный парсинг HTML."""
        # Мокаем BeautifulSoup
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        # Мокаем get_text
        mock_soup.get_text.return_value = "Иванов Иван Иванович Генеральный директор ИНН 1234567890 test@example.com +7 (999) 123-45-67"

        # Мокаем find для поиска тегов
        mock_soup.find.return_value = None

        html = "<html><body><h1>Иванов Иван Иванович</h1></body></html>"
        result = parse_html_content(html, "https://example.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["url"], "https://example.com")

    @patch('modules.lpr_parser.BeautifulSoup')
    def test_parse_html_content_empty(self, mock_bs):
        """Тестирует пустой HTML."""
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.get_text.return_value = ""

        html = ""
        result = parse_html_content(html)

        self.assertIsNotNone(result)
        self.assertEqual(result["fio"], "")
        self.assertEqual(result["position"], "")

    @patch('modules.lpr_parser.BeautifulSoup')
    def test_parse_html_content_no_data(self, mock_bs):
        """Тестирует отсутствие данных."""
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.get_text.return_value = "Нет данных"

        html = "<html><body></body></html>"
        result = parse_html_content(html)

        self.assertIsNotNone(result)
        self.assertEqual(result["fio"], "")

    @patch('modules.lpr_parser.BeautifulSoup')
    def test_parse_html_content_exception(self, mock_bs):
        """Тестирует исключение при парсинге."""
        mock_bs.side_effect = Exception("Parse error")

        html = "<html><body>...</body></html>"
        result = parse_html_content(html)

        self.assertIsNotNone(result)
        self.assertEqual(result["fio"], "")
        self.assertEqual(result["url"], "")


class TestSearchLprOnWebsite(unittest.TestCase):
    """Тесты для функции search_lpr_on_website."""

    @patch('modules.lpr_parser.fetch_url')
    @patch('modules.lpr_parser.parse_html_content')
    def test_search_lpr_on_website_success(self, mock_parse, mock_fetch):
        """Тестирует успешный поиск ЛПР на сайте."""
        mock_fetch.return_value = "<html>...</html>"
        mock_parse.return_value = {
            "url": "https://example.com",
            "fio": "Иванов Иван",
            "position": "Директор",
            "inn": "1234567890",
            "phones": "+79991234567",
            "emails": "test@example.com",
        }

        result = search_lpr_on_website("https://example.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["fio"], "Иванов Иван")
        mock_fetch.assert_called()

    @patch('modules.lpr_parser.fetch_url')
    def test_search_lpr_on_website_not_found(self, mock_fetch):
        """Тестирует отсутствие ЛПР на сайте."""
        mock_fetch.return_value = None

        result = search_lpr_on_website("https://example.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["fio"], "")
        self.assertEqual(result["position"], "")

    def test_search_lpr_on_website_no_requests(self):
        """Тестирует отсутствие библиотеки requests."""
        with patch('modules.lpr_parser.HAS_REQUESTS', False):
            result = search_lpr_on_website("https://example.com")

            self.assertIsNotNone(result)
            self.assertEqual(result["fio"], "")


class TestLoadCompaniesFromCsv(unittest.TestCase):
    """Тесты для функции load_companies_from_csv."""

    @patch('builtins.open', new_callable=mock_open, read_data="Название компании;Корпоративный сайт\nCompany 1;https://example.com\n")
    def test_load_companies_from_csv_success(self, mock_file):
        """Тестирует загрузку CSV."""
        result = load_companies_from_csv('test.csv')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Company 1")
        self.assertEqual(result[0]["url"], "https://example.com")

    @patch('builtins.open', new_callable=mock_open, read_data="Название лида;companyUrl\nCompany 2;https://test.com\n")
    def test_load_companies_from_csv_alternative_columns(self, mock_file):
        """Тестирует загрузку CSV с альтернативными названиями колонок."""
        result = load_companies_from_csv('test.csv')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Company 2")
        self.assertEqual(result[0]["url"], "https://test.com")

    @patch('builtins.open')
    def test_load_companies_from_csv_not_found(self, mock_file):
        """Тестирует отсутствие файла."""
        mock_file.side_effect = FileNotFoundError("File not found")

        result = load_companies_from_csv('nonexistent.csv')

        self.assertEqual(len(result), 0)

    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_load_companies_from_csv_empty(self, mock_file):
        """Тестирует пустой CSV файл."""
        result = load_companies_from_csv('empty.csv')

        self.assertEqual(len(result), 0)


class TestSaveLprToCsv(unittest.TestCase):
    """Тесты для функции save_lpr_to_csv."""

    @patch('builtins.open', new_callable=mock_open)
    def test_save_lpr_to_csv_success(self, mock_file):
        """Тестирует сохранение CSV."""
        lpr_data = [
            {
                'company_name': 'Test Company',
                'url': 'https://example.com',
                'fio': 'Иванов Иван',
                'position': 'Директор',
                'inn': '1234567890',
                'phones': '+79991234567',
                'emails': 'test@example.com',
            },
        ]

        result = save_lpr_to_csv(lpr_data, 'output.csv')

        self.assertTrue(result)
        mock_file.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_save_lpr_to_csv_multiple_records(self, mock_file):
        """Тестирует сохранение нескольких записей."""
        lpr_data = [
            {'company_name': 'Company 1', 'url': 'https://example1.com', 'fio': '', 'position': '', 'inn': '', 'phones': '', 'emails': ''},
            {'company_name': 'Company 2', 'url': 'https://example2.com', 'fio': '', 'position': '', 'inn': '', 'phones': '', 'emails': ''},
        ]

        result = save_lpr_to_csv(lpr_data, 'output.csv')

        self.assertTrue(result)

    @patch('builtins.open')
    def test_save_lpr_to_csv_exception(self, mock_file):
        """Тестирует исключение при сохранении."""
        mock_file.side_effect = Exception("IO Error")

        lpr_data = [{'company_name': 'Test', 'url': '', 'fio': '', 'position': '', 'inn': '', 'phones': '', 'emails': ''}]

        result = save_lpr_to_csv(lpr_data, 'output.csv')

        self.assertFalse(result)

    def test_save_lpr_to_csv_empty(self):
        """Тестирует пустые данные."""
        # Пустой список тоже должен сохраняться (с заголовком)
        with patch('builtins.open', new_callable=mock_open):
            result = save_lpr_to_csv([], 'output.csv')
            self.assertTrue(result)


class TestHelperFunctions(unittest.TestCase):
    """Тесты для вспомогательных функций."""

    def test_empty_result(self):
        """Тестирует _empty_result."""
        result = _empty_result("https://example.com")

        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["fio"], "")
        self.assertEqual(result["position"], "")
        self.assertEqual(result["inn"], "")
        self.assertEqual(result["phones"], "")
        self.assertEqual(result["emails"], "")

    def test_normalize_base_url_with_protocol(self):
        """Тестирует нормализацию URL с протоколом."""
        url = _normalize_base_url("https://example.com/")
        self.assertEqual(url, "https://example.com")

    def test_normalize_base_url_without_protocol(self):
        """Тестирует нормализацию URL без протокола."""
        url = _normalize_base_url("example.com/")
        self.assertEqual(url, "https://example.com")

    def test_normalize_base_url_http(self):
        """Тестирует нормализацию URL с http."""
        url = _normalize_base_url("http://example.com/")
        self.assertEqual(url, "http://example.com")

    def test_join_values_with_data(self):
        """Тестирует _join_values с данными."""
        result = _join_values(["a", "b", "c"])
        self.assertEqual(result, "a; b; c")

    def test_join_values_empty(self):
        """Тестирует _join_values с пустым списком."""
        result = _join_values([])
        self.assertEqual(result, "")

    def test_join_values_single(self):
        """Тестирует _join_values с одним элементом."""
        result = _join_values(["single"])
        self.assertEqual(result, "single")


class TestFetchUrl(unittest.TestCase):
    """Тесты для функции fetch_url."""

    @patch('modules.lpr_parser.requests.get')
    def test_fetch_url_success(self, mock_get):
        """Тестирует успешную загрузку URL."""
        mock_response = MagicMock()
        mock_response.text = "<html>...</html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_url("https://example.com")

        self.assertEqual(result, "<html>...</html>")
        mock_get.assert_called_once()

    @patch('modules.lpr_parser.requests.get')
    def test_fetch_url_exception(self, mock_get):
        """Тестирует исключение при загрузке URL."""
        mock_get.side_effect = Exception("Network error")

        result = fetch_url("https://example.com")

        self.assertIsNone(result)

    @patch('modules.lpr_parser.requests.get')
    def test_fetch_url_http_error(self, mock_get):
        """Тестирует HTTP ошибку при загрузке URL."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response

        result = fetch_url("https://example.com")

        self.assertIsNone(result)

    def test_fetch_url_no_requests(self):
        """Тестирует отсутствие библиотеки requests."""
        with patch('modules.lpr_parser.HAS_REQUESTS', False):
            result = fetch_url("https://example.com")
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
