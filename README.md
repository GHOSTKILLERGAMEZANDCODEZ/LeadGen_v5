# LeadGen v5 — Система автоматизации лидогенерации

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Десктопная система для автоматизации лидогенерации в холодных продажах**

Система обрабатывает выгрузки компаний из Яндекс.Карт/2GIS через сервис Webbee AI, преобразует «сырые» данные в очищенный CSV и готовит их к импорту в Битрикс24.

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Быстрый старт](#-быстрый-старт)
- [Структура проекта](#-структура-проекта)
- [Архитектура](#-архитектура)
- [Инструкция по использованию](#-инструкция-по-использованию)
- [Конфигурация](#-конфигурация)
- [API](#-api)
- [База данных](#-база-данных)
- [Тестирование](#-тестирование)
- [Устранение проблем](#-устранение-проблем)
- [Вклад в проект](#-вклад-в-проект)
- [Лицензия](#-лицензия)

---

## ✨ Возможности

### Обработка данных
- ✅ Загрузка TSV/CSV/JSON файлов от Webbee AI
- ✅ Очистка и нормализация телефонных номеров (конвертация из научной нотации)
- ✅ Удаление дубликатов по номерам телефонов
- ✅ Распределение лидов по менеджерам (round-robin)
- ✅ Маппинг данных в формат Битрикс24 (64 колонки)
- ✅ Экспорт в CSV с кодировкой UTF-8 с BOM

### Интеграции
- ✅ REST API Битрикс24 (вебхуки)
- ✅ Аналитика из Битрикс24 (загрузка LEAD.csv, DEAL.csv)
- ✅ Генератор ссылок Яндекс.Карт по сегментам
- ✅ Парсинг ЛПР (ФИО, должности, ИНН, телефоны, email)

### Интерфейс
- ✅ PySide6 интерфейс с тёмной темой
- ✅ Sidebar навигация с анимацией
- ✅ Drag & Drop загрузка файлов
- ✅ Предпросмотр данных с пагинацией
- ✅ Прогресс-бар обработки
- ✅ Мониторинг менеджеров в реальном времени

### Данные
- ✅ SQLite база данных для хранения статистики
- ✅ История обработок файлов
- ✅ Экспорт отчётов в Excel (openpyxl)
- ✅ Генерация диаграмм (matplotlib)

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
# Скопируйте шаблон переменных окружения
copy .env.example .env
```

Отредактируйте `.env` и добавьте ваш вебхук Битрикс24:

```env
BITRIX_WEBHOOK_URL=https://your-company.bitrix24.ru/rest/1/your_webhook_code/
```

### 3. Запуск приложения

```bash
python main.py
```

---

## 📁 Структура проекта

```
LeadGen_v5/
├── main.py                          # Точка входа (PySide6 QApplication)
├── config.json                      # Настройки приложения
├── .env.example                     # Шаблон переменных окружения
├── requirements.txt                 # Зависимости Python
├── README.md                        # Пользовательская документация
├── QWEN.md                          # Контекст для AI-агентов
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
│   │   └── processing_service.py    # Сервисный слой обработки
│   ├── phone_validator.py           # Валидация/нормализация телефонов
│   ├── data_processor.py            # Загрузка, очистка, объединение файлов
│   ├── bitrix_mapper.py             # Маппинг в 64 колонки Битрикс24
│   ├── bitrix_webhook.py            # REST API Битрикс24 (вебхуки)
│   ├── bitrix_analytics.py          # Аналитика из Битрикс24
│   ├── chart_generator.py           # Генерация диаграмм (matplotlib)
│   ├── report_exporter.py           # Экспорт отчётов в Excel (openpyxl)
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
│   ├── db_manager.py                # Менеджер БД (обёртка)
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

## 🏗 Архитектура

### Слои приложения

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer (PySide6)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Pages       │  │ Components  │  │ Threads         │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Service Layer (ProcessingService)          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Dependency Injection Container                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Business Logic Layer (modules/)           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Data        │  │ Bitrix      │  │ Validators      │ │
│  │ Processor   │  │ Mapper      │  │                 │ │
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
- **Pages** — страницы приложения (HomePage, ProcessingPage, etc.)
- **Components** — переиспользуемые компоненты (FileLoader, CircularProgress)
- **Threads** — фоновые потоки обработки (ProcessingThread, ExportThread)
- **Styles** — таблицы стилей и цветовые темы

### 2. Service Layer (`core/`, `modules/services/`)

Сервисный слой для абстракции между GUI и бизнес-логикой:
- **DependencyContainer** — централизованное управление зависимостями
- **ProcessingService** — сервис обработки лидов

### 3. Business Logic Layer (`modules/`)

Обработка данных, маппинг, валидация:
- **phone_validator.py** — нормализация телефонов
- **data_processor.py** — загрузка и обработка файлов
- **bitrix_mapper.py** — маппинг в формат Битрикс24
- **bitrix_webhook.py** — REST API интеграция
- **bitrix_analytics.py** — аналитика из Битрикс24
- **chart_generator.py** — генерация графиков
- **report_exporter.py** — экспорт в Excel
- **lpr_parser.py** — парсинг ЛПР
- **exceptions.py** — иерархия исключений

### 4. Data Access Layer (`database/`)

SQLite операции:
- **db_manager.py** — менеджер подключений
- **models.py** — SQL модели и функции

### 5. Utilities (`utils/`)

Логирование, конфигурация, вспомогательные функции:
- **logger.py** — настройка логирования
- **config_loader.py** — загрузка конфигурации
- **url_cleaner.py** — очистка URL от UTM
- **url_generator.py** — генератор URL Яндекс.Карт

---

## 📖 Инструкция по использованию

### Шаг 1: Настройка переменных окружения

1. Скопируйте `.env.example` в `.env`:
   ```bash
   copy .env.example .env
   ```

2. Добавьте URL вебхука Битрикс24 в файл `.env`:
   ```env
   BITRIX_WEBHOOK_URL=https://your-company.bitrix24.ru/rest/1/your_webhook_code/
   ```

### Шаг 2: Загрузка файлов

1. Запустите приложение: `python main.py`
2. Перейдите на страницу **«Обработка файлов»**
3. Нажмите кнопку **«📁 Выбрать файлы (JSON/TSV/CSV)»** или перетащите файлы в область Drag & Drop
4. Файлы отобразятся в списке

### Шаг 3: Настройка менеджеров

1. В правой панели введите имена менеджеров (по одному на строку)
2. Валидация автоматически проверит:
   - Минимум 1 менеджер
   - Максимум 10 менеджеров
   - Длина имени от 2 до 50 символов
3. Нажмите **«Сохранить список менеджеров»**

### Шаг 4: Обработка данных

1. Нажмите кнопку **«Очистить и объединить»**
2. Дождитесь завершения обработки (прогресс-бар показывает статус)
3. Проверьте предпросмотр результатов

### Шаг 5: Экспорт в Битрикс24

1. Нажмите кнопку **«📤 Экспортировать для Битрикс»**
2. Выберите место сохранения файла
3. Импортируйте CSV в Битрикс24

---

## 📊 Дополнительные возможности

### 📈 Аналитика Битрикс24

1. Перейдите на вкладку **«Аналитика Битрикс»**
2. Загрузите файлы `LEAD.csv` и `DEAL.csv` из экспорта Битрикс24
3. Нажмите **«Запустить анализ»**
4. Просмотрите воронки, категории, менеджеров и причины отказа
5. Экспортируйте отчёт в Excel

### 🔗 Генератор ссылок Яндекс.Карт

1. Перейдите на вкладку **«Генератор ссылок»**
2. Введите поисковый запрос (сегмент)
3. Выберите города и районы
4. Нажмите **«Сгенерировать ссылки»**
5. Скопируйте или сохраните в CSV

### 👤 Поиск ЛПР

1. Перейдите на вкладку **«Поиск ЛПР»**
2. Загрузите CSV файл со списком компаний
3. Нажмите **«Запустить поиск ЛПР»**
4. Получите ФИО, должности, ИНН, телефоны и email ЛПР

### 📈 Мониторинг менеджеров

1. Перейдите на вкладку **«Мониторинг менеджеров»**
2. Настройте URL вебхука Битрикс24
3. Нажмите **«Проверить и загрузить»**
4. Просмотрите распределение лидов по менеджерам
5. Исключите менеджеров из распределения при необходимости

---

## ⚙️ Конфигурация

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

## 🔌 API

### BitrixWebhookClient

Клиент для работы с REST API Битрикс24 через вебхуки.

#### Инициализация

```python
from modules.bitrix_webhook import BitrixWebhookClient

client = BitrixWebhookClient(
    webhook_url="https://your-company.bitrix24.ru/rest/1/webhook_code/",
    config=config
)
```

#### Основные методы

##### `test_connection() -> bool`

Проверяет подключение к Битрикс24.

```python
if client.test_connection():
    print("Подключение успешно")
```

##### `get_new_leads() -> list[dict]`

Получает новые лиды из Битрикс24.

```python
leads = client.get_new_leads()
for lead in leads:
    print(f"Лид: {lead['TITLE']}, Телефон: {lead['PHONE']}")
```

##### `get_managers() -> list[dict]`

Получает список менеджеров (пользователей Битрикс24).

```python
managers = client.get_managers()
for manager in managers:
    print(f"Менеджер: {manager['NAME']} {manager['LAST_NAME']}")
```

##### `assign_lead(lead_id: str, manager_id: str) -> bool`

Назначает лида на менеджера.

```python
success = client.assign_lead(lead_id="123", manager_id="456")
```

##### `update_lead_status(lead_id: str, status: str) -> bool`

Обновляет статус лида.

```python
success = client.update_lead_status(lead_id="123", status="В работе")
```

#### Обработка ошибок

```python
from modules.exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookConnectionError
)

try:
    leads = client.get_new_leads()
except BitrixWebhookNotFoundError:
    logger.error("Вебхук не найден")
except BitrixWebhookForbiddenError:
    logger.error("Нет прав доступа")
except BitrixWebhookRateLimitError:
    logger.warning("Превышен лимит запросов, ждём 1 секунду")
    time.sleep(1)
except BitrixWebhookConnectionError:
    logger.error("Нет подключения к интернету")
```

---

## 🗄 База данных

### Схема SQLite

#### Таблица `statistics`

Информация о загрузках файлов.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Первичный ключ |
| filename | TEXT | Имя файла |
| rows_processed | INTEGER | Количество обработанных строк |
| duplicates_removed | INTEGER | Количество удалённых дубликатов |
| processing_time_ms | INTEGER | Время обработки (мс) |
| created_at | TIMESTAMP | Дата и время создания |

#### Таблица `managers`

Список активных менеджеров.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | TEXT | Имя менеджера |
| is_active | BOOLEAN | Активен ли менеджер |
| created_at | TIMESTAMP | Дата добавления |

#### Таблица `processing_history`

История обработок файлов.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Первичный ключ |
| filename | TEXT | Имя файла |
| rows_processed | INTEGER | Количество строк |
| duplicates_removed | INTEGER | Удалённые дубликаты |
| processing_time_ms | INTEGER | Время обработки |
| created_at | TIMESTAMP | Дата обработки |

### DatabaseManager

#### Основные методы

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

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Запуск всех тестов
pytest tests/

# Запуск с отчётом о покрытии
pytest tests/ --cov=. --cov-report=html

# Запуск конкретных тестов
pytest tests/test_phone_validator.py
pytest tests/test_processing_service.py
```

### Покрытие тестами

| Модуль | Тесты | Покрытие |
|--------|-------|----------|
| phone_validator.py | 9 тестов | ~95% |
| data_processor.py | 4 теста | ~85% |
| bitrix_mapper.py | 4 теста | ~90% |
| processing_service.py | 8 тестов | ~92% |
| exceptions.py | 19 тестов | ~100% |

### Написание тестов

```python
# tests/test_example.py
import pytest
from modules.phone_validator import clean_phone

def test_clean_phone_valid():
    assert clean_phone("79991234567") == "79991234567"

def test_clean_phone_scientific():
    assert clean_phone(7.8005001695e+10) == "78005001695"

def test_clean_phone_invalid():
    assert clean_phone("123") is None
```

---

## 🐛 Устранение проблем

### Ошибка «No module named 'PySide6'»

```bash
pip install --upgrade PySide6
```

### Ошибка «No module named 'matplotlib'»

```bash
pip install matplotlib
```

### Ошибка кодировки при загрузке файла

Убедитесь, что файл в кодировке UTF-8. При необходимости конвертируйте.

### Ошибка «BITRIX_WEBHOOK_URL not set»

1. Убедитесь, что файл `.env` существует
2. Проверьте, что `BITRIX_WEBHOOK_URL` указан в `.env`
3. Перезапустите приложение

### Drag & Drop не работает

Убедитесь, что приложение запущено от имени администратора (Windows UAC может блокировать).

### Приложение не видит файлы

Проверьте, что файлы находятся в директории `data/input` или выбирайте через диалог.

---

## 🤝 Вклад в проект

### Стиль кода

- **Именование**: snake_case для функций/переменных, PascalCase для классов
- **Типизация**: Type hints для всех функций (Python 3.10+ синтаксис)
- **Docstrings**: Google-style docstrings для публичных функций
- **Логирование**: Использовать `logging.getLogger(__name__)` в каждом модуле

### Процесс разработки

1. Создайте ветку для новой функции
2. Напишите тесты
3. Реализуйте функциональность
4. Запустите тесты и линтеры
5. Создайте pull request

### Коммиты

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: добавление экспорта в Excel
fix: исправление ошибки валидации телефонов
docs: обновление документации API
refactor: рефакторинг ProcessingService
test: добавление тестов для bitrix_webhook
```

---

## 📄 Лицензия

Внутренняя разработка DIRECT-LINE.

## 📞 Поддержка

По вопросам обращайтесь к разработчику проекта.

---

**Версия**: 5.1.0
**Дата обновления**: 20 марта 2026 г.

---

## 🆕 Последние изменения (5.1.0)

### Генератор ссылок Яндекс.Карт

- **Новая компоновка интерфейса**: сегмент+результаты слева, города справа
- **Часовые пояса городов**: автоматическое определение времени для каждого города
- **Диалог управления городами**: удобное добавление/удаление городов и районов
- **Сохранение выбранных городов**: между сессиями приложения

### Главная страница

- **Логотип приложения**: визуальный элемент на HomePage
- **Glassmorphism эффекты**: полупрозрачные карточки с размытием
- **Улучшенная типографика**: обновлённые шрифты и отступы

### Улучшения

- Удалено дублирование кнопок «Добавить город»
- Перемещено управление городами из настроек в генератор ссылок
- Добавлены стили glassmorphism для современных эффектов
