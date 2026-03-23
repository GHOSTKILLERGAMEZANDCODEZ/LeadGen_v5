# Архитектура приложения LeadGen v5

Документ описывает архитектуру, принципы проектирования и взаимодействие компонентов приложения.

**Версия документа:** 1.1
**Дата обновления:** 20 марта 2026 г.

---

## Последние изменения (5.1.0)

### GUI

- **Генератор ссылок**: новая компоновка с QSplitter (сегмент+результаты слева, города справа)
- **Часовые пояса**: функция `get_city_timezone()` в utils
- **Диалог управления городами**: модальное окно для редактирования списка городов
- **HomePage**: добавлен логотип приложения
- **Glassmorphism стили**: новые переменные темы (`GLASS_CARD_BG`, `GLASS_BORDER`, etc.)

### Удалено

- Управление городами из настроек (перемещено в диалог генератора ссылок)
- Дублирование кнопок "Добавить город"

---

## Обзор

**LeadGen v5** — десктопная система автоматизации лидогенерации на PySide6 для обработки выгрузок компаний из Яндекс.Карт/2GIS через Webbee AI с последующим импортом в Битрикс24.

### Ключевые характеристики

- **Архитектурный стиль**: Многослойная архитектура (Layered Architecture)
- **Паттерны**: Dependency Injection, Service Layer, Repository
- **Тип приложения**: Десктопное (PySide6)
- **База данных**: SQLite (локальная)
- **Интеграции**: Битрикс24 (REST API), Яндекс.Карты, Webbee AI

---

## Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                              │
│                           (gui/)                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  MainWindow                                                       │  │
│  │  ┌────────────┐  ┌────────────────────────────────────────────┐  │  │
│  │  │  Sidebar   │  │  QStackedWidget                            │  │  │
│  │  │            │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  • Home    │  │  │  Pages                               │  │  │  │
│  │  │  • Process │  │  │  • HomePage                          │  │  │  │
│  │  │  • Analyze │  │  │  • ProcessingPage                    │  │  │  │
│  │  │  • Links   │  │  │  • AnalyticsPage                     │  │  │  │
│  │  │  • LPR     │  │  │  • LinkGeneratorPage                 │  │  │  │
│  │  │  • Monitor │  │  │  • LPRFinderPage                     │  │  │  │
│  │  │  • Settings│  │  │  • ManagerMonitorPage                │  │  │  │
│  │  │            │  │  │  • SettingsPage                      │  │  │  │
│  │  └────────────┘  │  └──────────────────────────────────────┘  │  │  │
│  │                  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │  Components                 │  Threads                     │  │  │
│  │  │  • CircularProgress         │  • ProcessingThread          │  │  │
│  │  │  • FileLoader (D&D)         │  • ExportThread              │  │  │
│  │  │  • FileList                 │                              │  │  │
│  │  │  • PreviewTable             │  Utils                       │  │  │
│  │  │                             │  • ErrorHandler              │  │  │
│  │  │                             │  • ThreadHelpers             │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                   │
│                      (core/, modules/services/)                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  DependencyContainer          │  ProcessingService               │  │
│  │  ┌──────────────────────┐     │  ┌──────────────────────────┐   │  │
│  │  │ • get_db_manager()   │────▶│  │ • process_files()        │   │  │
│  │  │ • get_processing_... │     │  │ • export_to_csv()        │   │  │
│  │  │ • get_bitrix_client()│     │  │                          │   │  │
│  │  └──────────────────────┘     │  └──────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                               │
│                         (modules/)                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Data         │ │ Bitrix       │ │ Phone        │ │ Chart        │  │
│  │ Processor    │ │ Mapper       │ │ Validator    │ │ Generator    │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Bitrix       │ │ Report       │ │ LPR          │ │ Exceptions   │  │
│  │ Webhook      │ │ Exporter     │ │ Parser       │ │              │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                                 │
│                        (database/)                                      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  DatabaseManager              │  Models                          │  │
│  │  ┌──────────────────────┐     │  ┌──────────────────────────┐   │  │
│  │  │ • add_statistics()   │     │  │ • statistics table       │   │  │
│  │  │ • save_managers()    │     │  │ • managers table         │   │  │
│  │  │ • get_history()      │     │  │ • processing_history     │   │  │
│  │  └──────────────────────┘     │  └──────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (data/database.db)                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  Битрикс24       │  │  Яндекс.Карты    │  │  Webbee AI       │     │
│  │  REST API        │  │  URL Generator   │  │  JSON/TSV/CSV    │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Слои приложения

### 1. Presentation Layer (GUI)

**Назначение:** Взаимодействие с пользователем, отображение данных, обработка событий UI.

**Технологии:** PySide6 (Qt для Python)

**Компоненты:**

#### MainWindow (`gui/main_window.py`)
- Главное окно приложения
- Содержит Sidebar и QStackedWidget
- Управляет навигацией между страницами

#### Sidebar (`gui/sidebar.py`)
- Боковая навигационная панель
- Анимированные кнопки переходов
- Индикация активной страницы

#### Pages (`gui/pages/`)
- **HomePage** — главная страница с быстрыми переходами
- **ProcessingPage** — обработка файлов Webbee AI
- **AnalyticsPage** — аналитика Битрикс24
- **LinkGeneratorPage** — генератор ссылок Яндекс.Карт
- **LPRFinderPage** — поиск ЛПР
- **ManagerMonitorPage** — мониторинг менеджеров
- **SettingsPage** — настройки приложения

#### Components (`gui/components/`)
- **CircularProgress** — круговой индикатор прогресса
- **FileLoader** — загрузка файлов (Drag & Drop)
- **FileList** — список загруженных файлов
- **PreviewTable** — предпросмотр данных с пагинацией

#### Threads (`gui/threads/`)
- **ProcessingThread** — фоновая обработка файлов
- **ExportThread** — фоновый экспорт в CSV

#### Styles (`gui/styles/`)
- **theme.py** — цветовые переменные (тёмная тема)
- **stylesheet.py** — таблицы стилей для виджетов

### 2. Service Layer

**Назначение:** Абстракция между GUI и бизнес-логикой, управление зависимостями.

**Компоненты:**

#### DependencyContainer (`core/dependency_container.py`)
- Централизованное создание и управление сервисами
- Ленивая инициализация (создание по требованию)
- Внедрение зависимостей

```python
container = DependencyContainer()
processing_service = container.get_processing_service()
bitrix_client = container.get_bitrix_client()
```

#### ProcessingService (`modules/services/processing_service.py`)
- Сервис обработки лидов
- Координация между загрузкой, обработкой и экспортом
- Сохранение статистики в БД

```python
service = ProcessingService(db_manager, config)
df, stats = service.process_files(file_paths, managers)
output_path = service.export_to_csv(df, "output.csv")
```

### 3. Business Logic Layer

**Назначение:** Бизнес-правила, обработка данных, интеграции.

**Компоненты:**

#### Data Processor (`modules/data_processor.py`)
- Загрузка файлов (JSON/TSV/CSV)
- Очистка и нормализация данных
- Удаление дубликатов
- Распределение менеджеров (round-robin)

#### Phone Validator (`modules/phone_validator.py`)
- Очистка телефонных номеров
- Конвертация из научной нотации
- Валидация по формату
- Поддержка форматов: 7, 8, +7

#### Bitrix Mapper (`modules/bitrix_mapper.py`)
- Маппинг данных в 64 колонки Битрикс24
- Очистка URL от UTM-меток
- Очистка Telegram/VK usernames
- Экспорт в CSV (UTF-8 с BOM)

#### Bitrix Webhook (`modules/bitrix_webhook.py`)
- REST API клиент Битрикс24
- Получение лидов, сделок, компаний
- Назначение менеджеров
- Обновление статусов

#### Bitrix Analytics (`modules/bitrix_analytics.py`)
- Загрузка экспорта Битрикс24 (LEAD.csv, DEAL.csv)
- Построение воронок продаж
- Группировка по менеджерам, категориям, источникам

#### Chart Generator (`modules/chart_generator.py`)
- Генерация графиков (matplotlib)
- Воронки, круговые диаграммы, столбчатые графики

#### Report Exporter (`modules/report_exporter.py`)
- Экспорт отчётов в Excel (openpyxl)
- Форматирование, стилизация

#### LPR Parser (`modules/lpr_parser.py`)
- Парсинг ЛПР (ФИО, должности, ИНН)
- Поиск контактов

#### Exceptions (`modules/exceptions.py`)
- Иерархия исключений (10 типов)
- Специализированные ошибки для каждого модуля

### 4. Data Access Layer

**Назначение:** Работа с базой данных, хранение состояния.

**Компоненты:**

#### Database Manager (`database/db_manager.py`)
- Менеджер подключений SQLite
- CRUD операции для таблиц
- Транзакции

#### Models (`database/models.py`)
- SQL модели таблиц
- Инициализация схемы БД

#### Таблицы:
- **statistics** — статистика обработок
- **managers** — список менеджеров
- **processing_history** — история обработок

### 5. External Services

**Назначение:** Интеграция с внешними системами.

#### Битрикс24
- REST API через вебхуки
- Получение/создание лидов
- Управление сделками
- Аналитика

#### Яндекс.Карты
- Генерация URL для поиска
- Сегментация по городам/районам

#### Webbee AI
- Загрузка выгрузок компаний
- Форматы: JSON, TSV, CSV

---

## Принципы проектирования

### 1. Разделение ответственности (Separation of Concerns)

Каждый слой отвечает за свою задачу:
- **GUI** — только отображение и ввод
- **Service** — координация и управление зависимостями
- **Business Logic** — бизнес-правила
- **Data Access** — хранение данных

### 2. Внедрение зависимостей (Dependency Injection)

Зависимости создаются централизованно в `DependencyContainer`:

```python
# Плохо: создание зависимостей в GUI
db = DatabaseManager("data/database.db")
service = ProcessingService(db, config)

# Хорошо: получение из контейнера
container = DependencyContainer()
service = container.get_processing_service()
```

### 3. Инверсия зависимостей (Dependency Inversion)

Модули верхнего уровня не зависят от модулей нижнего уровня:

```python
# ProcessingService зависит от абстракции (IDatabaseManager),
# а не от конкретной реализации (DatabaseManager)
class ProcessingService:
    def __init__(self, db_manager: IDatabaseManager, config: dict):
        self._db = db_manager
```

### 4. Единственная ответственность (Single Responsibility)

Каждый класс решает одну задачу:
- `PhoneValidator` — только валидация телефонов
- `BitrixMapper` — только маппинг данных
- `ChartGenerator` — только генерация графиков

### 5. Открытость/Закрытость (Open/Closed)

Модули открыты для расширения, но закрыты для изменений:

```python
# Добавление нового типа графика не требует изменения ChartGenerator
class ChartGenerator:
    def create_custom_chart(self, chart_type: str, data: dict):
        # Расширение через конфигурацию
        pass
```

---

## Взаимодействие компонентов

### Поток обработки файлов

```
1. Пользователь перетаскивает файлы в FileLoader
         │
         ▼
2. FileLoader отправляет сигнал files_dropped(paths)
         │
         ▼
3. ProcessingPage получает пути к файлам
         │
         ▼
4. ProcessingPage создаёт ProcessingThread
         │
         ▼
5. ProcessingThread вызывает ProcessingService.process_files()
         │
         ▼
6. ProcessingService:
   - Валидирует файлы
   - Вызывает merge_files() (Data Processor)
   - Вызывает map_to_bitrix() (Bitrix Mapper)
   - Сохраняет статистику (DatabaseManager)
         │
         ▼
7. ProcessingThread отправляет сигнал finished(df, stats)
         │
         ▼
8. ProcessingPage отображает результат в PreviewTable
```

### Поток экспорта в Битрикс24

```
1. Пользователь нажимает «Экспортировать»
         │
         ▼
2. ProcessingPage создаёт ExportThread
         │
         ▼
3. ExportThread вызывает export_to_bitrix_csv(df, path)
         │
         ▼
4. BitrixMapper экспортирует DataFrame в CSV
         │
         ▼
5. ExportThread отправляет сигнал finished(filepath)
         │
         ▼
6. ProcessingPage показывает уведомление об успехе
```

### Поток работы с Битрикс24

```
1. Пользователь настраивает вебхук в SettingsPage
         │
         ▼
2. ManagerMonitorPage получает вебхук из конфига
         │
         ▼
3. Вызывается BitrixWebhookClient.get_managers()
         │
         ▼
4. Делается HTTP POST запрос к API Битрикс24
         │
         ▼
5. Получается список менеджеров
         │
         ▼
6. ManagerMonitorPage отображает менеджеров в таблице
```

---

## Управление состоянием

### Конфигурация

**config.json** хранит настройки приложения:
- Настройки обработки телефонов
- Настройки путей
- Настройки UI
- Настройки Битрикс24 (кроме вебхука)

**.env** хранит чувствительные данные:
- `BITRIX_WEBHOOK_URL` — вебхук Битрикс24
- `LOG_LEVEL` — уровень логирования

### База данных

**SQLite** хранит состояние приложения:
- История обработок файлов
- Список активных менеджеров
- Статистика обработок

### Сигналы PySide6

Компоненты GUI взаимодействуют через сигналы:

```python
# Определение сигнала
class ProcessingThread(QThread):
    progress = Signal(int)
    finished = Signal(DataFrame, dict)
    error = Signal(str)

# Подключение
thread = ProcessingThread()
thread.progress.connect(self.update_progress_bar)
thread.finished.connect(self.handle_finished)
thread.error.connect(self.handle_error)
```

---

## Безопасность

### Хранение секретов

- **Вебхуки Битрикс24** хранятся в `.env` (игнорируется git)
- **НЕ сохраняются** в `config.json` или логах

### Валидация ввода

- Все пользовательские данные валидируются
- SQL-инъекции предотвращаются параметризованными запросами
- Path Traversal предотвращается проверкой путей

### Обработка ошибок

```python
try:
    # операция
except BitrixWebhookNotFoundError:
    logger.error("Вебхук не найден")
    show_error("Проверьте URL вебхука")
except ProcessingError as e:
    logger.error(f"Ошибка обработки: {e}", exc_info=True)
    show_error("Ошибка обработки данных")
except Exception as e:
    logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
    show_error("Произошла непредвиденная ошибка")
```

---

## Производительность

### Оптимизации

1. **Фоновые потоки:** обработка не блокирует UI
2. **Пагинация таблиц:** отображение максимум 100 строк
3. **Векторизация pandas:** все операции с данными векторизованы
4. **Ленивая инициализация:** сервисы создаются по требованию
5. **Кэширование:** экземпляры сервисов кэшируются в DI Container

### Ограничения

- Обработка файлов >10000 строк может занимать несколько минут
- Большие изображения в графиках могут замедлять отрисовку
- API Битрикс24 имеет rate limiting (2 запроса/сек)

---

## Масштабируемость

### Горизонтальное масштабирование

В текущей архитектуре возможно:
- Вынесение обработки в отдельный процесс (multiprocessing)
- Вынесение тяжёлых задач в Celery очереди
- Разделение на микросервисы (обработка, аналитика, вебхуки)

### Вертикальное масштабирование

- Увеличение лимита памяти для pandas
- Оптимизация SQL запросов
- Индексация часто используемых полей

---

## Тестирование

### Уровни тестирования

1. **Модульные тесты** (`tests/test_*.py`)
   - Тесты отдельных функций и классов
   - Покрытие: ~54 теста

2. **Интеграционные тесты** (TODO)
   - Тесты взаимодействия между модулями
   - Тесты с реальной БД

3. **E2E тесты** (TODO)
   - Тесты полного цикла через GUI
   - pytest-qt для автоматизации

### Моки и стабы

```python
# Моки для тестирования сервисного слоя
@pytest.fixture
def mock_db_manager():
    db = Mock()
    db.add_processing_record = Mock()
    return db

@pytest.fixture
def mock_config():
    return {"processing": {"phone_format": "7"}}

def test_process_files(mock_db_manager, mock_config):
    service = ProcessingService(mock_db_manager, mock_config)
    # Тестирование без реальной БД
```

---

## Расширение

### Добавление новой страницы

1. Создать `gui/pages/new_page.py`:

```python
from PySide6.QtWidgets import QWidget

class NewPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Инициализация UI
        pass
```

2. Добавить в `gui/main_window.py`:

```python
from gui.pages.new_page import NewPage

# В конструкторе MainWindow
self.stack.addWidget(NewPage())  # Добавление страницы
```

3. Добавить кнопку в `gui/sidebar.py`

### Добавление новой интеграции

1. Создать модуль в `modules/new_integration.py`:

```python
class NewIntegration:
    def __init__(self, config: dict):
        self._config = config
    
    def fetch_data(self) -> dict:
        # Получение данных
        pass
```

2. Добавить исключения в `modules/exceptions.py`

3. Написать тесты в `tests/test_new_integration.py`

4. Обновить документацию

---

## Будущие улучшения

### Краткосрочные (1-3 месяца)

- [ ] E2E тесты для GUI
- [ ] Поддержка множественных порталов Битрикс24
- [ ] Уведомления в Telegram
- [ ] Планировщик задач

### Долгосрочные (3-6 месяцев)

- [ ] Миграция на асинхронную архитектуру (asyncio)
- [ ] Веб-интерфейс вместо десктопного
- [ ] Машинное обучение для классификации лидов
- [ ] Распределённая обработка (Celery)

---

## Глоссарий

| Термин | Определение |
|--------|-------------|
| **Лид** | Потенциальный клиент (компания) |
| **ЛПР** | Лицо, Принимающее Решение |
| **Webbee AI** | Сервис парсинга Яндекс.Карт/2GIS |
| **Битрикс24** | CRM система для управления лидами |
| **Вебхук** | URL для вызова API Битрикс24 |
| **Round-robin** | Циклическое распределение |
| **DI Container** | Контейнер внедрения зависимостей |

---

**Версия документа:** 1.0  
**Дата обновления:** 20 марта 2026 г.
