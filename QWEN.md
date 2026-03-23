# LeadGen v5 — Контекст для AI-агентов

## Обзор проекта

**LeadGen_v5** — десктопная система автоматизации лидогенерации для холодных продаж. Обрабатывает выгрузки компаний из Яндекс.Карт/2GIS через сервис Webbee AI, преобразует «сырые» данные в очищенный CSV, готовый к импорту в Битрикс24.

### Ключевые возможности

- Загрузка TSV/CSV/JSON файлов от Webbee AI
- Очистка и нормализация телефонных номеров (конвертация из научной нотации, удаление нецифровых символов)
- Удаление дубликатов по номерам телефонов
- Распределение лидов по менеджерам (round-robin)
- Маппинг данных в формат Битрикс24 (64 колонки)
- PySide6 интерфейс с тёмной темой
- SQLite база данных для хранения статистики
- REST API интеграция с Битрикс24 (вебхуки)
- Dependency Injection для упрощения тестирования
- Сервисный слой для абстракции бизнес-логики

### Технологии

- **Язык**: Python 3.11.9+
- **GUI**: PySide6 >= 6.5.0
- **Data Processing**: pandas >= 2.0.0
- **HTTP Client**: requests >= 2.28.0
- **Парсинг**: beautifulsoup4 >= 4.11.0
- **Визуализация**: matplotlib >= 3.7.0
- **Конфигурация**: python-dotenv >= 1.0.0
- **База данных**: SQLite3 (встроенный)
- **Excel**: openpyxl >= 3.1.0

---

## Структура проекта

```
LeadGen_v5/
├── main.py                          # Точка входа (PySide6 QApplication)
├── config.json                      # Настройки приложения
├── .env / .env.example              # Переменные окружения (вебхуки, пути)
├── requirements.txt                 # Зависимости Python
├── README.md                        # Пользовательская документация
├── QWEN.md                          # Этот файл (контекст для AI)
├── CHANGELOG.md                     # История изменений
├── mypy.ini                         # Настройки типизации
├── pytest.ini                       # Настройки pytest
│
├── core/                            # Ядро приложения
│   ├── __init__.py
│   └── dependency_container.py      # Dependency Injection Container
│
├── modules/                         # Бизнес-логика
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── processing_service.py    # Сервисный слой обработки (DI)
│   ├── phone_validator.py           # Валидация/нормализация телефонов
│   ├── data_processor.py            # Загрузка, очистка, объединение файлов
│   ├── bitrix_mapper.py             # Маппинг в 64 колонки Битрикс24
│   ├── bitrix_webhook.py            # REST API Битрикс24 (вебхуки)
│   ├── bitrix_analytics.py          # Аналитика из Битрикс24
│   ├── chart_generator.py           # Генерация диаграмм
│   ├── report_exporter.py           # Экспорт отчётов в Excel
│   ├── lpr_parser.py                # Парсинг ЛПР (лицо, принимающее решение)
│   └── exceptions.py                # Иерархия исключений (10 типов)
│
├── gui/                             # PySide6 интерфейс
│   ├── __init__.py
│   ├── main_window.py               # Главное окно с sidebar навигацией
│   ├── sidebar.py                   # Боковая панель навигации
│   ├── preview_table.py             # Предпросмотр данных
│   ├── progress_bar.py              # Прогресс-бар
│   ├── pages/                       # Страницы приложения
│   │   ├── __init__.py
│   │   ├── home_page.py             # Главная страница
│   │   ├── processing_page.py       # Страница обработки файлов
│   │   ├── analytics_page.py        # Аналитика Битрикс
│   │   ├── link_generator_page.py   # Генератор ссылок
│   │   ├── lpr_finder_page.py       # Поиск ЛПР
│   │   ├── manager_monitor_page.py  # Мониторинг менеджеров
│   │   └── settings_page.py         # Настройки
│   ├── components/                  # Переиспользуемые компоненты
│   │   ├── __init__.py
│   │   ├── circular_progress.py     # Круговой прогресс
│   │   ├── file_list.py             # Список файлов
│   │   └── file_loader.py           # Загрузка файлов Drag&Drop
│   ├── styles/                      # Стили и темы
│   │   ├── __init__.py
│   │   ├── stylesheet.py            # Таблицы стилей
│   │   └── theme.py                 # Цветовые переменные
│   ├── threads/                     # Потоки обработки
│   │   ├── __init__.py
│   │   └── processing_thread.py     # ProcessingThread, ExportThread
│   └── utils/                       # Утилиты GUI
│       ├── __init__.py
│       ├── error_handler.py         # Обработка ошибок
│       └── thread_helpers.py        # Помощники потоков
│
├── database/                        # База данных SQLite
│   ├── __init__.py
│   ├── db_manager.py                # Менеджер БД (обёртка над SQLite)
│   └── models.py                    # Модели таблиц (statistics, managers, history)
│
├── utils/                           # Утилиты
│   ├── __init__.py
│   ├── logger.py                    # Настройка логирования
│   ├── config_loader.py             # Загрузка/сохранение конфигурации
│   ├── url_cleaner.py               # Очистка URL от UTM-меток
│   ├── url_generator.py             # Генератор URL Яндекс.Карт
│   └── windows_blur.py              # Windows DWM blur эффект
│
├── data/                            # Данные приложения
│   ├── input/                       # Входные файлы (JSON/TSV/CSV)
│   ├── output/                      # Выходные CSV файлы
│   ├── reports/                     # Отчёты Excel
│   ├── logs/                        # Логи приложения (*.log)
│   └── database.db                  # SQLite база данных
│
├── docs/                            # Документация
│   ├── CODEMAPS/                    # Карты проекта
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   ├── database.md
│   │   ├── services.md
│   │   └── integrations.md
│   ├── api/                         # API документация
│   │   └── bitrix-webhook.md
│   ├── architecture.md              # Архитектурный обзор
│   └── database-schema.md           # Схема базы данных
│
└── tests/                           # Модульные тесты
    ├── __init__.py
    ├── conftest.py                  # Конфигурация pytest
    ├── test_phone_validator.py      # 9 тестов
    ├── test_data_processor.py       # 4 теста
    ├── test_bitrix_mapper.py        # 4 теста
    ├── test_bitrix_webhook.py       # Тесты вебхуков
    ├── test_bitrix_analytics.py     # Тесты аналитики
    ├── test_chart_generator.py      # Тесты графиков
    ├── test_lpr_parser.py           # Тесты парсера ЛПР
    ├── test_report_exporter.py      # Тесты экспорта
    ├── test_processing_service.py   # 8 тестов сервиса
    ├── test_exceptions.py           # 19 тестов исключений
    └── test_gui/                    # GUI тесты
```

---

## Архитектура приложения

### Слои приложения

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer (PySide6)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Pages       │  │ Components  │  │ Threads         │ │
│  │ (pages/)    │  │ (comps/)    │  │ (threads/)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Service Layer (ProcessingService)          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Dependency Injection Container                  │   │
│  │ - get_processing_service()                      │   │
│  │ - get_bitrix_client()                           │   │
│  │ - get_db_manager()                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Business Logic Layer (modules/)           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Data        │  │ Bitrix      │  │ Validators      │ │
│  │ Processor   │  │ Mapper      │  │ (phone, etc.)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Data Access Layer (database/)              │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │ DB Manager  │  │ Models      │                      │
│  └─────────────┘  └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 1. GUI Layer (`gui/`)

PySide6 виджеты, обработка событий UI:

- **pages/** — страницы приложения:
  - `home_page.py` — главная страница с быстрыми переходами
  - `processing_page.py` — обработка файлов (520 строк)
  - `analytics_page.py` — аналитика Битрикс (996 строк)
  - `link_generator_page.py` — генератор ссылок
  - `lpr_finder_page.py` — поиск ЛПР
  - `manager_monitor_page.py` — мониторинг менеджеров
  - `settings_page.py` — настройки (952 строки)

- **components/** — переиспользуемые компоненты:
  - `circular_progress.py` — круговой прогресс-бар
  - `file_list.py` — список файлов
  - `file_loader.py` — загрузка Drag&Drop (284 строки)

- **styles/** — стили и темы:
  - `stylesheet.py` — таблицы стилей
  - `theme.py` — цветовые переменные (BACKGROUND_PRIMARY, ACCENT_CYAN, etc.)

- **threads/** — фоновые потоки:
  - `processing_thread.py` — ProcessingThread, ExportThread (220 строк)

- **utils/** — утилиты GUI:
  - `error_handler.py` — обработка ошибок
  - `thread_helpers.py` — ThreadCleanupMixin

### 2. Service Layer (`core/`, `modules/services/`)

Сервисный слой для абстракции между GUI и бизнес-логикой:

#### DependencyContainer (`core/dependency_container.py`)

Централизованное управление зависимостями:

```python
from core.dependency_container import DependencyContainer

container = DependencyContainer()
processing_service = container.get_processing_service()
bitrix_client = container.get_bitrix_client()
db_manager = container.get_db_manager()
```

**Ленивая инициализация:** сервисы создаются только при первом вызове.

#### ProcessingService (`modules/services/processing_service.py`)

Сервис обработки лидов:

```python
from modules.services.processing_service import ProcessingService

service = ProcessingService(db_manager, config)

# Обработка файлов
df_bitrix, stats = service.process_files(file_paths, managers)

# Экспорт в CSV
output_path = service.export_to_csv(df_bitrix, "output.csv")
```

**Методы:**
- `process_files(file_paths, managers)` — обработка файлов
- `export_to_csv(df, filepath)` — экспорт в CSV
- `_validate_files(file_paths)` — валидация файлов
- `_save_to_database(file_paths, stats)` — сохранение в БД

### 3. Business Logic Layer (`modules/`)

#### phone_validator.py

Валидация и нормализация телефонов:

```python
from modules.phone_validator import clean_phone, format_phone, validate_phone

# Очистка телефона
cleaned = clean_phone("7.8005001695e+10")  # "78005001695"

# Форматирование
formatted = format_phone("79991234567", format="8")  # "89991234567"

# Валидация
is_valid = validate_phone("79991234567")  # True
```

**Правила обработки:**
- Конвертация из научной нотации (`7.8005001695e+10` → `78005001695`)
- Удаление всех нецифровых символов
- Номера короче 10 цифр или не начинающиеся с 7/8 — отклоняются
- Поддержка форматов: 7XXXXXXXXXX, 8XXXXXXXXXX, +7XXXXXXXXXX

#### data_processor.py

Загрузка и обработка файлов:

```python
from modules.data_processor import load_file, merge_files, remove_duplicates, assign_managers

# Загрузка одного файла
df = load_file("file.json")  # или .tsv, .csv

# Обработка нескольких файлов
df, stats = merge_files(["file1.json", "file2.json"], managers, processing_settings)

# Удаление дубликатов
df = remove_duplicates(df, remove_duplicates_flag=True)

# Распределение менеджеров
df = assign_managers(df, ["Менеджер 1", "Менеджер 2"])
```

#### bitrix_mapper.py

Маппинг в формат Битрикс24 (64 колонки):

```python
from modules.bitrix_mapper import map_to_bitrix, export_to_bitrix_csv

# Маппинг
df_bitrix = map_to_bitrix(df, stage="Новая заявка", source="Холодный звонок")

# Экспорт
export_to_bitrix_csv(df_bitrix, "output.csv")
```

**Особенности:**
- 64 колонки согласно шаблону Битрикс24
- Разделитель: `;` (точка с запятой)
- Кодировка: `utf-8-sig` (UTF-8 с BOM для Excel)
- Очистка URL от UTM-меток
- Очистка Telegram usernames (удаление URL, добавление @)
- Очистка ВКонтакте usernames

#### bitrix_webhook.py

REST API Битрикс24 через вебхуки:

```python
from modules.bitrix_webhook import BitrixWebhookClient

client = BitrixWebhookClient(webhook_url, config)

# Проверка подключения
if client.test_connection():
    print("Подключение успешно")

# Получение лидов
leads = client.get_new_leads()

# Получение менеджеров
managers = client.get_managers()

# Назначение лида
client.assign_lead(lead_id="123", manager_id="456")
```

#### bitrix_analytics.py

Аналитика из Битрикс24:

```python
from modules.bitrix_analytics import BitrixAnalytics

analytics = BitrixAnalytics()
analytics.load_lead_csv("LEAD.csv")
analytics.load_deal_csv("DEAL.csv")

# Анализ
funnel = analytics.build_funnel()
by_manager = analytics.group_by_manager()
by_category = analytics.group_by_category()
```

#### chart_generator.py

Генерация графиков (matplotlib):

```python
from modules.chart_generator import ChartGenerator

generator = ChartGenerator()

# Воронка продаж
generator.create_funnel_chart(stages, values, "funnel.png")

# Распределение по менеджерам
generator.create_pie_chart(managers, counts, "managers.png")

# Динамика по дням
generator.create_line_chart(dates, values, "dynamics.png")
```

#### report_exporter.py

Экспорт отчётов в Excel (openpyxl):

```python
from modules.report_exporter import ReportExporter

exporter = ReportExporter()
exporter.export_analytics_report(
    funnel_data,
    manager_data,
    category_data,
    "report.xlsx"
)
```

#### lpr_parser.py

Парсинг ЛПР (лицо, принимающее решение):

```python
from modules.lpr_parser import LPRParser

parser = LPRParser()
lpr_data = parser.parse_company(company_name, inn)

# Возвращает:
# - ФИО
# - Должность
# - ИНН
# - Телефоны
# - Email
```

#### exceptions.py

Иерархия исключений:

```
LeadGenError (базовое)
├── SecurityError
├── BitrixWebhookError
│   ├── BitrixWebhookNotFoundError
│   ├── BitrixWebhookForbiddenError
│   ├── BitrixWebhookRateLimitError
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

### 4. Data Access Layer (`database/`)

#### db_manager.py

Менеджер базы данных:

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/database.db")

# Сохранение статистики
db.add_statistics(
    filename="file.json",
    rows_processed=100,
    duplicates_removed=10,
    processing_time_ms=500
)

# Сохранение менеджеров
db.save_managers(["Менеджер 1", "Менеджер 2"])

# Получение активных менеджеров
managers = db.get_active_managers()

# Получение истории
history = db.get_history(limit=10)
```

#### models.py

Модели таблиц и инициализация БД:

```python
from database.models import init_database

init_database("data/database.db")
```

**Таблицы:**
- `statistics` — информация о загрузках файлов
- `managers` — список активных менеджеров
- `processing_history` — история обработок

### 5. Utilities (`utils/`)

#### logger.py

Настройка логирования:

```python
from utils.logger import setup_logger

logger = setup_logger("my_module", log_file="data/logs/app.log")
logger.info("Сообщение")
```

#### config_loader.py

Загрузка конфигурации:

```python
from utils.config_loader import load_config, save_config

config = load_config("config.json")
save_config(config, "config.json")
```

#### url_cleaner.py

Очистка URL от UTM-меток:

```python
from utils.url_cleaner import clean_url

clean = clean_url("https://example.com?utm_source=google&utm_campaign=test")
# "https://example.com"
```

#### url_generator.py

Генератор URL Яндекс.Карт:

```python
from utils.url_generator import generate_yandex_maps_url

url = generate_yandex_maps_url(
    query="Рестораны",
    city="Москва",
    district="ЦАО"
)
```

---

## Запуск и разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск приложения

```bash
python main.py
```

### Запуск тестов

```bash
pytest tests/
# или
python -m unittest discover tests/
```

### Проверка типов

```bash
mypy .
```

---

## Конфигурация

### Переменные окружения (`.env`)

```env
# Битрикс24 Вебхук
BITRIX_WEBHOOK_URL=https://your-company.bitrix24.ru/rest/1/your_webhook_code/

# Настройки обработки
PHONE_FORMAT=7
MIN_PHONE_LENGTH=10
REMOVE_DUPLICATES=true
IGNORE_PHONE_2=false

# Настройки UI
UI_THEME=dark
UI_FONT_SIZE=10

# Пути
INPUT_DIR=data/input
OUTPUT_DIR=data/output
DATABASE_PATH=data/database.db

# Логирование
LOG_LEVEL=INFO
```

### Настройки приложения (`config.json`)

```json
{
    "managers": ["Елена Юматова"],
    "processing": {
        "phone_format": "7",
        "remove_duplicates": true,
        "min_phone_length": 10,
        "ignore_phone_2": false
    },
    "paths": {
        "input_dir": "data/input",
        "output_dir": "data/output",
        "database": "data/database.db"
    },
    "ui": {
        "theme": "dark",
        "font_family": "Cambria",
        "font_size": 10
    },
    "bitrix": {
        "stage": "Новая заявка",
        "source": "Холодный звонок",
        "service_type": "ГЦК"
    },
    "bitrix_webhook": {
        "webhook_url": "",
        "status_id": "Новая заявка",
        "max_leads_per_manager": 75,
        "excluded_managers": []
    },
    "regions": ["Москва", "Санкт-Петербург"],
    "city_districts": {},
    "log_level": "INFO"
}
```

---

## Архитектурные принципы

### Ключевые потоки данных

1. **Загрузка файлов** → `data_processor.load_file()` → DataFrame
2. **Обработка** → `ProcessingService.process_files()` → очистка телефонов → удаление дубликатов → распределение менеджеров
3. **Маппинг** → `bitrix_mapper.map_to_bitrix()` → 64 колонки
4. **Экспорт** → `bitrix_mapper.export_to_bitrix_csv()` → CSV файл
5. **Сохранение статистики** → `DatabaseManager.add_processing_record()` → SQLite

### Многопоточность

- Обработка файлов в фоновых потоках (не блокирует UI)
- Сигналы PySide6: `progress`, `finished`, `error` для обновления UI
- `ProcessingThread` — поток обработки файлов
- `ExportThread` — поток экспорта в CSV

---

## Конвенции разработки

### Стиль кода

- **Именование**: snake_case для функций/переменных, PascalCase для классов
- **Типизация**: Type hints для всех функций (Python 3.10+ синтаксис)
- **Docstrings**: Google-style docstrings для публичных функций
- **Логирование**: Использовать `logging.getLogger(__name__)` в каждом модуле

### Пример типизации

```python
def clean_phone(
    phone: str | float | int | None,
    phone_format: str = "7",
    min_length: int = 10,
) -> Optional[str]:
    """Очищает и нормализует телефонный номер."""
```

### Обработка ошибок

```python
try:
    # операция
except Exception as e:
    logger.error(f"Описание ошибки: {e}", exc_info=True)
    return None  # или raise
```

### Тестирование

- Модульные тесты в `tests/` через `pytest`
- Тестирование граничных условий (пустые значения, невалидные данные)
- Запуск тестов перед коммитом

### Безопасность

- **НЕ сохранять** чувствительные данные (вебхуки, токены) в `config.json`
- Использовать переменные окружения (`.env`) для секретов
- Файл `.env` исключён из git (`.gitignore`)

---

## Основные модули (детали)

### Правила обработки телефонов

- **Целевой формат**: 11 цифр, начиная с 7 (например, `79991234567`)
- Конвертация из научной нотации (`7.8005001695e+10` → `78005001695`)
- Удаление всех нецифровых символов
- Номера короче 10 цифр или не начинающиеся с 7/8 — удаляются
- Дубликаты по телефонам — удаляются (остаётся первое вхождение)

### Выходной формат для Битрикс24

CSV файл с 64 колонками, включая:

| Поле | Значение |
|------|----------|
| TITLE | Название лида (`[Category 0] - [Название]`) |
| PHONE | Рабочий телефон (очищенный) |
| COMPANY_PHONE | Мобильный телефон |
| ADDRESS | Адрес компании |
| COMPANY_WEB | Сайт (без UTM-меток) |
| STATUS_ID | «Новая заявка» |
| SOURCE_ID | «Холодный звонок» |
| COMMENTS | Дополнительная информация |

---

## GUI Архитектура

### MainWindow

Главное окно с:
- Sidebar навигацией (анимированная)
- QStackedWidget для переключения страниц
- Порядком страниц:
  1. HomePage — главная с быстрыми переходами
  2. ProcessingPage — обработка файлов
  3. AnalyticsPage — аналитика Битрикс
  4. LinkGeneratorPage — генератор ссылок Яндекс.Карт
  5. LPRFinderPage — поиск ЛПР
  6. ManagerMonitorPage — мониторинг менеджеров
  7. SettingsPage — настройки

### Стили и темы

- `gui/styles/theme.py` — цветовые переменные (BACKGROUND_PRIMARY, ACCENT_CYAN, etc.)
- `gui/styles/stylesheet.py` — таблицы стилей для виджетов
- Тёмная тема по умолчанию

---

## Дополнительные возможности

### Аналитика Битрикс24
- Загрузка `LEAD.csv` и `DEAL.csv` из экспорта Битрикс
- Построение воронок, категорий, менеджеров
- Экспорт отчётов в Excel

### Генератор ссылок Яндекс.Карт
- Генерация URL для поиска по сегментам
- Выбор городов и районов
- Экспорт ссылок в CSV

### Поиск ЛПР
- Парсинг ФИО, должностей, ИНН, телефонов, email
- Интеграция с обработанными данными

### Мониторинг менеджеров
- Загрузка данных из Битрикс24 через вебхук
- Распределение лидов по менеджерам
- Исключение менеджеров из распределения

---

## Частые проблемы и решения

| Проблема | Решение |
|----------|---------|
| `No module named 'PySide6'` | `pip install --upgrade PySide6` |
| `No module named 'matplotlib'` | `pip install matplotlib` |
| Ошибка кодировки | Убедиться, что файлы в UTF-8 |
| `BITRIX_WEBHOOK_URL not set` | Проверить наличие `.env` и переменной |
| Drag & Drop не работает | Запустить от имени администратора (Windows UAC) |

---

## Логирование

Логи сохраняются в `data/logs/leadgen_YYYYMMDD.log`:
- Уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR` (настраивается в `.env`)
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

---

## Расширение функциональности

### Добавление новой страницы

1. Создать класс страницы в `gui/pages/` (наследник `QWidget`)
2. Добавить импорт в `gui/main_window.py`
3. Добавить страницу в `QStackedWidget` через `addWidget()`
4. Добавить кнопку в `gui/sidebar.py`

### Добавление новой настройки

1. Добавить в `config.json` (если не чувствительные данные)
2. Добавить в `.env.example` (если чувствительные данные)
3. Обновить `gui/pages/settings_page.py` для UI

### Добавление новой колонки Битрикс

1. Обновить `BITRIX_COLUMNS` в `modules/bitrix_mapper.py`
2. Добавить маппинг в `map_to_bitrix()`
3. Обновить документацию

---

## Интеграция с AI-агентами

### Доступные специализированные агенты

- **python-reviewer** — ревью кода Python (PEP 8, type hints, безопасность)
- **code-reviewer** — общий code review (архитектура, паттерны, best practices)
- **security-reviewer** — проверка безопасности (аутентификация, ввод данных, API, секреты, OWASP)
- **database-reviewer** — SQL, миграции, дизайн схем, PostgreSQL/SQLite
- **tdd-guide** — TDD методология, написание тестов перед кодом
- **planner** — планирование сложных фич, рефакторинг, разбивка на этапы
- **architect** — проектирование архитектуры, технические решения
- **build-error-resolver** — ошибки TypeScript/Python, проблемы сборки
- **doc-updater** — документация, codemaps, README, guides
- **refactor-cleaner** — удаление мёртвого кода, дубликатов, консолидация

### Когда использовать агентов

- После написания нового модуля → **python-reviewer**
- Перед коммитом изменений в бизнес-логике → **python-reviewer**, **security-reviewer**
- При рефакторинге структуры проекта → **architect**, **refactor-cleaner**
- При добавлении новых тестов → **tdd-guide**
- При обновлении документации → **doc-updater**
- При планировании новой фичи → **planner**

---

## Контакты

Внутренняя разработка DIRECT-LINE. По вопросам обращаться к разработчику проекта.

---

**Версия**: 5.1.0
**Дата обновления**: 20 марта 2026 г.

---

## Последние изменения (5.1.0 — март 2026)

### GUI

#### Генератор ссылок Яндекс.Карт
- **Новая компоновка**: сегмент+результаты слева, города справа (QSplitter)
- **Часовые пояса городов**: функция `get_city_timezone(city)` в `utils/city_timezones.py`
- **Диалог управления городами**: модальное окно для редактирования списка городов и районов
- **Сохранение выбранных городов**: между сессиями приложения

#### HomePage
- **Логотип приложения**: визуальный элемент на главной странице
- **Glassmorphism эффекты**: карточки с полупрозрачным фоном
- **Улучшенная типографика**: обновлённые шрифты и отступы

#### Настройки
- **Удалено управление городами из настроек**: перемещено в диалог генератора ссылок
- **Удалено дублирование кнопок "Добавить город"**: единая точка управления

#### Стили
- **Glassmorphism theme**: новые переменные в `gui/styles/theme.py`
  - `GLASS_CARD_BG` — фон стеклянных карточек
  - `GLASS_BORDER` — цвет границы стекла
  - `GLASS_BUTTON_BG` — фон стеклянных кнопок
  - `GLASS_HOVER` — эффект наведения

### Утилиты

#### city_timezones.py
```python
from utils.city_timezones import get_city_timezone

tz = get_city_timezone("Москва")  # Europe/Moscow
tz = get_city_timezone("Владивосток")  # Asia/Vladivostok
```

### Изменения в архитектуре GUI

#### LinkGeneratorPage
- Использование `QSplitter` для разделения панелей
- Левая панель: сегмент, результаты, кнопки действий
- Правая панель: scrollable список городов с чекбоксами
- Модальный диалог для управления городами

#### HomePage
- Добавлен виджет логотипа
- Обновлена структура приветственной секции
- Применены glassmorphism стили

---

**Версия**: 5.1.0
**Дата обновления**: 20 марта 2026 г.
