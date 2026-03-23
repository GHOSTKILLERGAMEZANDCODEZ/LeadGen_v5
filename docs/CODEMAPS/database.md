# Code Map: Database

Карта базы данных приложения LeadGen v5.

## Обзор

Приложение использует **SQLite3** (встроенный в Python) для хранения локальных данных.

```
database/
├── __init__.py
├── db_manager.py           # Менеджер базы данных
└── models.py               # Модели таблиц и инициализация
```

---

## Схема базы данных

### Таблица `statistics`

Информация о загрузках файлов.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Первичный ключ |
| filename | TEXT NOT NULL | Имя файла |
| rows_processed | INTEGER NOT NULL | Количество обработанных строк |
| duplicates_removed | INTEGER NOT NULL | Количество удалённых дубликатов |
| processing_time_ms | INTEGER NOT NULL | Время обработки (мс) |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Дата и время создания |

**SQL:**

```sql
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `managers`

Список активных менеджеров.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Первичный ключ |
| name | TEXT NOT NULL UNIQUE | Имя менеджера |
| is_active | BOOLEAN DEFAULT 1 | Активен ли менеджер |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Дата добавления |

**SQL:**

```sql
CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `processing_history`

История обработок файлов.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Первичный ключ |
| filename | TEXT NOT NULL | Имя файла |
| rows_processed | INTEGER NOT NULL | Количество строк |
| duplicates_removed | INTEGER NOT NULL | Удалённые дубликаты |
| processing_time_ms | INTEGER NOT NULL | Время обработки |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Дата обработки |

**SQL:**

```sql
CREATE TABLE IF NOT EXISTS processing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## DatabaseManager

### Класс `DatabaseManager`

Менеджер базы данных в `database/db_manager.py`.

**Инициализация:**

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/database.db")
```

### Методы

#### `add_statistics()`

Сохраняет статистику обработки.

```python
def add_statistics(
    self,
    filename: str,
    rows_processed: int,
    duplicates_removed: int,
    processing_time_ms: int,
) -> None
```

**Пример:**

```python
db.add_statistics(
    filename="file1.json",
    rows_processed=100,
    duplicates_removed=10,
    processing_time_ms=500
)
```

#### `save_managers()`

Сохраняет список менеджеров.

```python
def save_managers(
    self,
    managers: list[str],
) -> None
```

**Пример:**

```python
db.save_managers(["Менеджер 1", "Менеджер 2", "Менеджер 3"])
```

#### `get_active_managers()`

Получает активных менеджеров.

```python
def get_active_managers(self) -> list[str]
```

**Пример:**

```python
managers = db.get_active_managers()
# ["Менеджер 1", "Менеджер 2"]
```

#### `add_processing_record()`

Добавляет запись в историю обработок.

```python
def add_processing_record(
    self,
    filename: str,
    rows_processed: int,
    duplicates_removed: int,
    processing_time_ms: int,
) -> None
```

**Пример:**

```python
db.add_processing_record(
    filename="file1.json",
    rows_processed=100,
    duplicates_removed=10,
    processing_time_ms=500
)
```

#### `get_history()`

Получает историю обработок.

```python
def get_history(
    self,
    limit: int = 10,
) -> list[dict]
```

**Пример:**

```python
history = db.get_history(limit=10)
for record in history:
    print(f"{record['filename']}: {record['rows_processed']} строк")
```

---

## Модели (models.py)

### Функция `init_database()`

Инициализирует базу данных, создаёт таблицы.

```python
from database.models import init_database

init_database("data/database.db")
```

**SQL операции:**

```python
def init_database(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            rows_processed INTEGER NOT NULL,
            duplicates_removed INTEGER NOT NULL,
            processing_time_ms INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица managers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица processing_history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            rows_processed INTEGER NOT NULL,
            duplicates_removed INTEGER NOT NULL,
            processing_time_ms INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
```

---

## Взаимодействие с другими модулями

```
┌─────────────────────────────────────────────────────────┐
│                   ProcessingService                     │
│  (сервисный слой)                                       │
└─────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│                   DatabaseManager                       │
│  (менеджер базы данных)                                 │
│                                                         │
│  - add_statistics()                                     │
│  - save_managers()                                      │
│  - get_active_managers()                                │
│  - add_processing_record()                              │
│  - get_history()                                        │
└─────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│                      SQLite3                            │
│  (файл data/database.db)                                │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ statistics   │  │ managers     │  │ processing_  │ │
│  │              │  │              │  │ history      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Примеры использования

### Полный цикл работы с БД

```python
from database.db_manager import DatabaseManager
from database.models import init_database

# Инициализация БД
init_database("data/database.db")

# Создание менеджера БД
db = DatabaseManager("data/database.db")

# Сохранение менеджеров
db.save_managers(["Елена Юматова", "Менеджер 2"])

# Получение активных менеджеров
active_managers = db.get_active_managers()
print(f"Активные менеджеры: {active_managers}")

# После обработки файла сохранение статистики
db.add_statistics(
    filename="webbee_export.json",
    rows_processed=500,
    duplicates_removed=25,
    processing_time_ms=1200
)

# Добавление записи в историю
db.add_processing_record(
    filename="webbee_export.json",
    rows_processed=500,
    duplicates_removed=25,
    processing_time_ms=1200
)

# Получение истории
history = db.get_history(limit=5)
for record in history:
    print(f"{record['filename']}: {record['rows_processed']} строк, "
          f"{record['duplicates_removed']} дубликатов удалено")
```

### Интеграция с ProcessingService

```python
from core.dependency_container import DependencyContainer

container = DependencyContainer()

# Получение сервисов
processing_service = container.get_processing_service()
db_manager = container.get_db_manager()

# Обработка файлов
df, stats = processing_service.process_files(
    file_paths=["file.json"],
    managers=["Менеджер 1"]
)

# Статистика автоматически сохраняется в БД через ProcessingService
```

---

## Тестирование

### Тесты DatabaseManager

```python
# tests/test_db_manager.py
import pytest
import tempfile
import os
from database.db_manager import DatabaseManager
from database.models import init_database

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    init_database(db_path)
    yield db_path
    os.unlink(db_path)

def test_save_managers(temp_db):
    db = DatabaseManager(temp_db)
    db.save_managers(["Менеджер 1", "Менеджер 2"])
    
    managers = db.get_active_managers()
    assert len(managers) == 2
    assert "Менеджер 1" in managers

def test_add_statistics(temp_db):
    db = DatabaseManager(temp_db)
    db.add_statistics(
        filename="test.json",
        rows_processed=100,
        duplicates_removed=5,
        processing_time_ms=500
    )
    
    history = db.get_history()
    assert len(history) == 1
    assert history[0]['rows_processed'] == 100
```

---

## Миграции

### Версия 1.0 (текущая)

```sql
-- Таблица statistics
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица managers
CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица processing_history
CREATE TABLE IF NOT EXISTS processing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Будущие миграции

```sql
-- TODO: Добавить таблицу для настроек пользователя
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TODO: Добавить таблицу для кэша ЛПР
CREATE TABLE IF NOT EXISTS lpr_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    inn TEXT,
    director_name TEXT,
    contacts TEXT,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Производительность

### Оптимизации

- **Индексы:** автоматические индексы на PRIMARY KEY
- **Транзакции:** пакетная запись в транзакциях
- **Соединение:** одно соединение на операцию

### Проблемы

- При большой истории (>10000 записей) замедляется выборка
- Решение: архивация старых записей (TODO)

---

## Будущие улучшения

- [ ] Архивация старых записей истории
- [ ] Поддержка PostgreSQL для multi-user режима
- [ ] Синхронизация с облаком
- [ ] Резервное копирование БД
- [ ] Статистика использования по дням/неделям
