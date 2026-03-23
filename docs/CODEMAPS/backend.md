# Code Map: Backend (Business Logic)

Карта backend модулей приложения LeadGen v5.

**Last Updated:** 2026-03-20
**Версия:** 5.1.0

## Обзор

Backend приложение представляет собой слой бизнес-логики, расположенный в директории `modules/`. Модули не зависят от GUI и могут использоваться независимо.

### Последние изменения (5.1.0)

- **utils/city_timezones.py**: функция `get_city_timezone(city)` для определения часового пояса
- **utils/config_loader.py**: улучшена поддержка вложенных конфигураций
- **Удалено**: управление городами из настроек (перемещено в GUI)

```
modules/
├── services/
│   └── processing_service.py    # Сервисный слой (DI)
│
├── phone_validator.py           # Валидация телефонов
├── data_processor.py            # Обработка данных
├── bitrix_mapper.py             # Маппинг Битрикс24
├── bitrix_webhook.py            # REST API Битрикс
├── bitrix_analytics.py          # Аналитика Битрикс
├── chart_generator.py           # Генерация графиков
├── report_exporter.py           # Экспорт в Excel
├── lpr_parser.py                # Парсинг ЛПР
└── exceptions.py                # Иерархия исключений
```

---

## Сервисный слой (modules/services/)

### processing_service.py

**Класс:** `ProcessingService`

Сервис для обработки лидов с абстракцией от GUI.

**Зависимости:**
- `IDatabaseManager` (протокол)
- `config` (dict)

**Методы:**

```python
class ProcessingService:
    def __init__(self, db_manager: IDatabaseManager, config: dict)
    
    def process_files(
        self,
        file_paths: list[str],
        managers: list[str],
    ) -> tuple[DataFrame, dict]
        """Обрабатывает файлы и возвращает результат для Битрикс."""
    
    def export_to_csv(
        self,
        df: DataFrame,
        filepath: str,
    ) -> str
        """Экспортирует DataFrame в CSV файл."""
```

**Пример использования:**

```python
from modules.services.processing_service import ProcessingService

service = ProcessingService(db_manager, config)

# Обработка
df_bitrix, stats = service.process_files(
    file_paths=["file1.json", "file2.json"],
    managers=["Менеджер 1", "Менеджер 2"]
)

# Экспорт
output_path = service.export_to_csv(df_bitrix, "output.csv")
```

---

## Обработка данных

### phone_validator.py

**Функции:**

```python
def clean_phone(
    phone: str | float | int | None,
    phone_format: str = "7",
    min_length: int = 10,
) -> Optional[str]
    """Очищает и нормализует телефонный номер."""

def format_phone(
    phone: str,
    format: str = "7",
) -> str
    """Форматирует телефон по заданному формату."""

def validate_phone(
    phone: str,
    min_length: int = 10,
) -> bool
    """Проверяет валидность телефона."""

def extract_phone_from_any(
    value: Any,
) -> Optional[str]
    """Извлекает телефон из любого типа данных."""
```

**Примеры:**

```python
from modules.phone_validator import clean_phone, format_phone

# Конвертация из научной нотации
clean_phone(7.8005001695e+10)  # "78005001695"

# Удаление нецифровых символов
clean_phone("+7 (999) 123-45-67")  # "79991234567"

# Форматирование
format_phone("79991234567", format="8")  # "89991234567"
format_phone("79991234567", format="+7")  # "+79991234567"
```

### data_processor.py

**Функции:**

```python
def load_file(
    filepath: str,
) -> DataFrame
    """Загружает JSON/TSV/CSV файл в DataFrame."""

def process_file(
    filepath: str,
    source_name: str,
    processing_settings: dict,
) -> tuple[DataFrame, dict]
    """Обрабатывает один файл."""

def merge_files(
    filepaths: list[str],
    managers: list[str],
    processing_settings: dict,
) -> tuple[DataFrame, dict]
    """Объединяет несколько файлов."""

def remove_duplicates(
    df: DataFrame,
    remove_duplicates_flag: bool,
) -> DataFrame
    """Удаляет дубликаты по телефонам."""

def assign_managers(
    df: DataFrame,
    managers: list[str],
) -> DataFrame
    """Распределяет лидов по менеджерам (round-robin)."""

def prepare_output_columns(
    df: DataFrame,
) -> DataFrame
    """Подготавливает итоговые колонки."""
```

**Пример использования:**

```python
from modules.data_processor import merge_files, remove_duplicates, assign_managers

# Обработка файлов
df, stats = merge_files(
    filepaths=["file1.json", "file2.json"],
    managers=["Менеджер 1", "Менеджер 2"],
    processing_settings={"phone_format": "7", "remove_duplicates": True}
)

# Удаление дубликатов
df = remove_duplicates(df, remove_duplicates_flag=True)

# Распределение менеджеров
df = assign_managers(df, ["Менеджер 1", "Менеджер 2"])
```

---

## Маппинг Битрикс24

### bitrix_mapper.py

**Константы:**

```python
BITRIX_COLUMNS = [
    "TITLE", "NAME", "SECOND_NAME", "LAST_NAME",
    "PHONE", "COMPANY_PHONE", "ADDRESS", "COMPANY_WEB",
    "STATUS_ID", "SOURCE_ID", "COMMENTS",
    # ... всего 64 колонки
]
```

**Функции:**

```python
def map_to_bitrix(
    df: DataFrame,
    stage: str = "Новая заявка",
    source: str = "Холодный звонок",
    service_type: str = "ГЦК",
) -> DataFrame
    """Маппит данные в формат Битрикс24 (64 колонки)."""

def export_to_bitrix_csv(
    df: DataFrame,
    filepath: str,
) -> bool
    """Экспортирует DataFrame в CSV для Битрикс24."""
```

**Пример:**

```python
from modules.bitrix_mapper import map_to_bitrix, export_to_bitrix_csv

# Маппинг
df_bitrix = map_to_bitrix(
    df,
    stage="Новая заявка",
    source="Холодный звонок",
    service_type="ГЦК"
)

# Экспорт
export_to_bitrix_csv(df_bitrix, "output.csv")
```

**Особенности:**
- Разделитель: `;` (точка с запятой)
- Кодировка: `utf-8-sig` (UTF-8 с BOM для Excel)
- Очистка URL от UTM-меток
- Очистка Telegram usernames
- Очистка ВКонтакте usernames

---

## REST API Битрикс24

### bitrix_webhook.py

**Класс:** `BitrixWebhookClient`

Клиент для работы с REST API Битрикс24 через вебхуки.

**Методы:**

```python
class BitrixWebhookClient:
    def __init__(self, webhook_url: str, config: dict)
    
    def test_connection(self) -> bool
        """Проверяет подключение к Битрикс24."""
    
    def get_new_leads(self) -> list[dict]
        """Получает новые лиды из Битрикс24."""
    
    def get_managers(self) -> list[dict]
        """Получает список менеджеров (пользователей)."""
    
    def assign_lead(self, lead_id: str, manager_id: str) -> bool
        """Назначает лида на менеджера."""
    
    def update_lead_status(self, lead_id: str, status: str) -> bool
        """Обновляет статус лида."""
    
    def get_lead(self, lead_id: str) -> dict
        """Получает лида по ID."""
    
    def create_lead(self, fields: dict) -> str
        """Создаёт нового лида."""
```

**Пример:**

```python
from modules.bitrix_webhook import BitrixWebhookClient

client = BitrixWebhookClient(webhook_url, config)

# Проверка подключения
if client.test_connection():
    print("Подключение успешно")

# Получение лидов
leads = client.get_new_leads()

# Назначение лида
client.assign_lead(lead_id="123", manager_id="456")
```

---

## Аналитика Битрикс24

### bitrix_analytics.py

**Класс:** `BitrixAnalytics`

Аналитика из экспорта Битрикс24.

**Методы:**

```python
class BitrixAnalytics:
    def load_lead_csv(self, filepath: str) -> None
        """Загружает LEAD.csv из экспорта Битрикс."""
    
    def load_deal_csv(self, filepath: str) -> None
        """Загружает DEAL.csv из экспорта Битрикс."""
    
    def build_funnel(self) -> dict
        """Строит воронку продаж."""
    
    def group_by_manager(self) -> DataFrame
        """Группирует по менеджерам."""
    
    def group_by_category(self) -> DataFrame
        """Группирует по категориям."""
    
    def group_by_source(self) -> DataFrame
        """Группирует по источникам."""
    
    def get_rejection_reasons(self) -> DataFrame
        """Получает причины отказа."""
```

**Пример:**

```python
from modules.bitrix_analytics import BitrixAnalytics

analytics = BitrixAnalytics()
analytics.load_lead_csv("LEAD.csv")
analytics.load_deal_csv("DEAL.csv")

# Анализ
funnel = analytics.build_funnel()
by_manager = analytics.group_by_manager()
```

---

## Визуализация

### chart_generator.py

**Класс:** `ChartGenerator`

Генерация графиков через matplotlib.

**Методы:**

```python
class ChartGenerator:
    def create_funnel_chart(
        self,
        stages: list[str],
        values: list[int],
        output_path: str,
    ) -> str
        """Создаёт воронку продаж."""
    
    def create_pie_chart(
        self,
        labels: list[str],
        values: list[float],
        output_path: str,
        title: str = "",
    ) -> str
        """Создаёт круговую диаграмму."""
    
    def create_bar_chart(
        self,
        labels: list[str],
        values: list[float],
        output_path: str,
        title: str = "",
    ) -> str
        """Создаёт столбчатую диаграмму."""
    
    def create_line_chart(
        self,
        x: list[str],
        y: list[float],
        output_path: str,
        title: str = "",
    ) -> str
        """Создаёт линейный график."""
```

---

## Экспорт в Excel

### report_exporter.py

**Класс:** `ReportExporter`

Экспорт отчётов в Excel через openpyxl.

**Методы:**

```python
class ReportExporter:
    def export_analytics_report(
        self,
        funnel_data: dict,
        manager_data: DataFrame,
        category_data: DataFrame,
        output_path: str,
    ) -> str
        """Экспортирует аналитический отчёт в Excel."""
    
    def export_leads_report(
        self,
        df: DataFrame,
        output_path: str,
    ) -> str
        """Экспортирует отчёт по лидам в Excel."""
```

---

## Парсинг ЛПР

### lpr_parser.py

**Класс:** `LPRParser`

Парсинг ЛПР (лицо, принимающее решение).

**Методы:**

```python
class LPRParser:
    def parse_company(
        self,
        company_name: str,
        inn: Optional[str] = None,
    ) -> dict
        """Парсит информацию о компании."""
    
    def extract_director(
        self,
        company_data: dict,
    ) -> Optional[str]
        """Извлекает директора из данных компании."""
    
    def find_contacts(
        self,
        company_name: str,
    ) -> dict
        """Находит контакты ЛПР."""
```

**Возвращает:**
- ФИО
- Должность
- ИНН
- Телефоны
- Email

---

## Исключения

### exceptions.py

**Иерархия:**

```
LeadGenError (базовое)
├── SecurityError
├── BitrixWebhookError
│   ├── BitrixWebhookNotFoundError (404)
│   ├── BitrixWebhookForbiddenError (403)
│   ├── BitrixWebhookRateLimitError (429)
│   ├── BitrixWebhookInvalidURLError
│   └── BitrixWebhookConnectionError
├── ProcessingError
├── ValidationError
└── ExportError
```

**Пример использования:**

```python
from modules.exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    ProcessingError,
    ValidationError
)

try:
    leads = client.get_new_leads()
except BitrixWebhookNotFoundError:
    logger.error("Вебхук не найден")
except BitrixWebhookForbiddenError:
    logger.error("Нет прав доступа")
except ProcessingError as e:
    logger.error(f"Ошибка обработки: {e}")
```

---

## Dependency Injection

### core/dependency_container.py

**Класс:** `DependencyContainer`

Контейнер зависимостей для централизованного создания сервисов.

**Методы:**

```python
class DependencyContainer:
    def __init__(self, config: dict | None = None)
    
    def get_db_manager(self) -> DatabaseManager
        """Возвращает менеджер базы данных."""
    
    def get_processing_service(self) -> ProcessingService
        """Возвращает сервис обработки данных."""
    
    def get_bitrix_client(self) -> BitrixWebhookClient
        """Возвращает клиент Битрикс24."""
```

**Ленивая инициализация:** сервисы создаются только при первом вызове.

**Пример:**

```python
from core.dependency_container import DependencyContainer

container = DependencyContainer()

# Сервисы создаются при первом вызове
processing_service = container.get_processing_service()
bitrix_client = container.get_bitrix_client()
db_manager = container.get_db_manager()
```

---

## Взаимодействие между модулями

```
┌─────────────────────────────────────────────────────────┐
│                   ProcessingService                     │
│  (сервисный слой, абстракция от GUI)                   │
└─────────────────────────────────────────────────────────┘
        │              │              │
        v              v              v
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Data         │ │ Bitrix       │ │ Phone        │
│ Processor    │ │ Mapper       │ │ Validator    │
└──────────────┘ └──────────────┘ └──────────────┘
        │              │
        v              v
┌──────────────┐ ┌──────────────┐
│ Bitrix       │ │ Bitrix       │
│ Webhook      │ │ Analytics    │
└──────────────┘ └──────────────┘
```

---

## Тестирование

### Модульные тесты

```python
# tests/test_phone_validator.py
def test_clean_phone_valid():
    assert clean_phone("79991234567") == "79991234567"

def test_clean_phone_scientific():
    assert clean_phone(7.8005001695e+10) == "78005001695"

def test_clean_phone_invalid():
    assert clean_phone("123") is None
```

### Тесты сервисного слоя

```python
# tests/test_processing_service.py
def test_process_files(mock_db_manager, mock_config):
    service = ProcessingService(mock_db_manager, mock_config)
    df, stats = service.process_files(["test.json"], ["Manager 1"])
    assert not df.empty
    assert stats["rows_processed"] > 0
```

---

## Расширение

### Добавление нового модуля

1. Создать файл `modules/new_module.py`:

```python
"""Описание модуля."""

import logging

logger = logging.getLogger(__name__)


class NewModule:
    """Класс модуля."""
    
    def __init__(self, config: dict):
        self._config = config
    
    def do_something(self, data: str) -> str:
        """Выполняет действие."""
        logger.info(f"Выполняется действие над: {data}")
        return data.upper()
```

2. Добавить исключения в `modules/exceptions.py` при необходимости

3. Написать тесты в `tests/test_new_module.py`

4. Обновить документацию

---

## Производительность

### Оптимизации

- **Pandas векторизация:** все операции с данными векторизованы
- **Потоковая обработка:** большие файлы обрабатываются частями
- **Кэширование:** результаты маппинга кэшируются

### Проблемы

- Обработка файлов >100MB может занимать несколько минут
- Решение: асинхронная обработка (TODO)

---

## Будущие улучшения

- [ ] Асинхронная обработка файлов
- [ ] Поддержка дополнительных источников данных
- [ ] Интеграция с amoCRM
- [ ] Машинное обучение для классификации лидов
- [ ] Распределённая обработка (Celery)

---

## Утилиты (utils/)

### city_timezones.py (5.1.0)

**Функция:** `get_city_timezone(city: str) -> str`

Определяет часовой пояс города.

```python
from utils.city_timezones import get_city_timezone

tz = get_city_timezone("Москва")  # "Europe/Moscow"
tz = get_city_timezone("Владивосток")  # "Asia/Vladivostok"
tz = get_city_timezone("Неизвестный город")  # "Europe/Moscow" (по умолчанию)
```

**Применение:**
- Генератор ссылок Яндекс.Карт (отображение времени для городов)
- Планировщик задач (будущая функция)

### config_loader.py

**Функции:**
- `load_config(path: str) -> dict` — загрузка конфигурации
- `save_config(config: dict, path: str)` — сохранение конфигурации

**Изменения в 5.1.0:**
- Улучшена поддержка вложенных конфигураций
- Добавлена обработка ошибок при загрузке

### url_cleaner.py

**Функция:** `clean_url(url: str) -> str`

Очищает URL от UTM-меток.

```python
from utils.url_cleaner import clean_url

clean = clean_url("https://example.com?utm_source=google&utm_campaign=test")
# "https://example.com"
```

### url_generator.py

**Функция:** `generate_yandex_maps_url(query: str, city: str, district: Optional[str] = None) -> str`

Генерирует URL для поиска Яндекс.Карт.

```python
from utils.url_generator import generate_yandex_maps_url

url = generate_yandex_maps_url("Рестораны", "Москва", "ЦАО")
# "https://yandex.ru/maps/213/moscow/search/Рестораны ЦАО/"
```

### windows_blur.py

**Функция:** `apply_blur_effect(hwnd: int)`

Применяет DWM blur эффект к окну (Windows).

```python
from utils.windows_blur import apply_blur_effect

apply_blur_effect(window.winId())
```
