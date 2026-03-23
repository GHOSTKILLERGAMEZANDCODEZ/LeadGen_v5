# Схема базы данных

База данных приложения LeadGen v5 использует **SQLite3**.

**Расположение:** `data/database.db`

**Версия документации:** 1.1
**Дата обновления:** 20 марта 2026 г.

---

## Последние изменения (5.1.0)

Изменения в схеме базы данных отсутствуют. Все изменения в версии 5.1.0 касаются только GUI и утилит.

---

## Обзор

База данных состоит из трёх таблиц:
- **statistics** — информация о загрузках файлов
- **managers** — список активных менеджеров
- **processing_history** — история обработок файлов

```
┌─────────────────────────────────────────────────────────┐
│                    database.db                          │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ statistics   │  │ managers     │  │ processing_  │ │
│  │              │  │              │  │ history      │ │
│  │ - id         │  │ - id         │  │ - id         │ │
│  │ - filename   │  │ - name       │  │ - filename   │ │
│  │ - rows_...   │  │ - is_active  │  │ - rows_...   │ │
│  │ - dups_...   │  │ - created_at │  │ - dups_...   │ │
│  │ - proc_...   │  │              │  │ - proc_...   │ │
│  │ - created_at │  │              │  │ - created_at │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Таблица `statistics`

Информация о загрузках файлов.

### Структура

| Колонка | Тип | Nullable | Default | Описание |
|---------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTOINCREMENT | Первичный ключ |
| filename | TEXT | NO | — | Имя файла |
| rows_processed | INTEGER | NO | — | Количество обработанных строк |
| duplicates_removed | INTEGER | NO | — | Количество удалённых дубликатов |
| processing_time_ms | INTEGER | NO | — | Время обработки (мс) |
| created_at | TIMESTAMP | YES | CURRENT_TIMESTAMP | Дата и время создания |

### SQL

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

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_statistics_filename ON statistics(filename);
CREATE INDEX IF NOT EXISTS idx_statistics_created_at ON statistics(created_at);
```

### Примеры данных

| id | filename | rows_processed | duplicates_removed | processing_time_ms | created_at |
|----|----------|----------------|-------------------|-------------------|------------|
| 1 | webbee_export.json | 500 | 25 | 1200 | 2026-03-20 10:00:00 |
| 2 | companies.tsv | 1000 | 50 | 2500 | 2026-03-20 11:30:00 |
| 3 | leads.csv | 250 | 10 | 600 | 2026-03-20 14:15:00 |

### Использование

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/database.db")

# Добавление записи
db.add_statistics(
    filename="webbee_export.json",
    rows_processed=500,
    duplicates_removed=25,
    processing_time_ms=1200
)
```

---

## Таблица `managers`

Список активных менеджеров.

### Структура

| Колонка | Тип | Nullable | Default | Описание |
|---------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTOINCREMENT | Первичный ключ |
| name | TEXT | NO | — | Имя менеджера (уникальное) |
| is_active | BOOLEAN | YES | 1 | Активен ли менеджер |
| created_at | TIMESTAMP | YES | CURRENT_TIMESTAMP | Дата добавления |

### SQL

```sql
CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_managers_name ON managers(name);
CREATE INDEX IF NOT EXISTS idx_managers_is_active ON managers(is_active);
```

### Примеры данных

| id | name | is_active | created_at |
|----|------|-----------|------------|
| 1 | Елена Юматова | 1 | 2026-03-01 09:00:00 |
| 2 | Менеджер 2 | 1 | 2026-03-05 10:30:00 |
| 3 | Менеджер 3 | 0 | 2026-03-10 14:00:00 |

### Использование

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/database.db")

# Сохранение менеджеров
db.save_managers(["Елена Юматова", "Менеджер 2", "Менеджер 3"])

# Получение активных менеджеров
active = db.get_active_managers()
# ["Елена Юматова", "Менеджер 2"]

# Деактивация менеджера (через SQL)
db.execute("UPDATE managers SET is_active = 0 WHERE name = ?", ("Менеджер 3",))
```

---

## Таблица `processing_history`

История обработок файлов.

### Структура

| Колонка | Тип | Nullable | Default | Описание |
|---------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTOINCREMENT | Первичный ключ |
| filename | TEXT | NO | — | Имя файла |
| rows_processed | INTEGER | NO | — | Количество обработанных строк |
| duplicates_removed | INTEGER | NO | — | Удалённые дубликаты |
| processing_time_ms | INTEGER | NO | — | Время обработки (мс) |
| created_at | TIMESTAMP | YES | CURRENT_TIMESTAMP | Дата обработки |

### SQL

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

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_processing_history_filename ON processing_history(filename);
CREATE INDEX IF NOT EXISTS idx_processing_history_created_at ON processing_history(created_at);
```

### Примеры данных

| id | filename | rows_processed | duplicates_removed | processing_time_ms | created_at |
|----|----------|----------------|-------------------|-------------------|------------|
| 1 | webbee_export.json | 500 | 25 | 1200 | 2026-03-20 10:00:00 |
| 2 | webbee_export.json | 1000 | 50 | 2500 | 2026-03-20 11:30:00 |
| 3 | companies.tsv | 250 | 10 | 600 | 2026-03-20 14:15:00 |
| 4 | webbee_export.json | 750 | 30 | 1800 | 2026-03-21 09:00:00 |

### Использование

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/database.db")

# Добавление записи
db.add_processing_record(
    filename="webbee_export.json",
    rows_processed=500,
    duplicates_removed=25,
    processing_time_ms=1200
)

# Получение истории
history = db.get_history(limit=10)

for record in history:
    print(f"{record['filename']}: {record['rows_processed']} строк, "
          f"{record['duplicates_removed']} дубликатов")
```

---

## ER-диаграмма

```
┌─────────────────────────────────────────────────────────┐
│                     DATABASE                            │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        v                   v                   v
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   statistics     │ │    managers      │ │ processing_...   │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ PK id            │ │ PK id            │ │ PK id            │
│    filename      │ │    name (UNIQUE) │ │    filename      │
│    rows_...      │ │    is_active     │ │    rows_...      │
│    dups_...      │ │    created_at    │ │    dups_...      │
│    proc_...      │ │                  │ │    proc_...      │
│    created_at    │ │                  │ │    created_at    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## DatabaseManager

### Класс `DatabaseManager`

**Расположение:** `database/db_manager.py`

### Методы

#### `__init__(db_path: str)`

Инициализирует подключение к базе данных.

```python
db = DatabaseManager("data/database.db")
```

#### `add_statistics(filename, rows_processed, duplicates_removed, processing_time_ms)`

Сохраняет статистику обработки.

```python
db.add_statistics(
    filename="file.json",
    rows_processed=100,
    duplicates_removed=10,
    processing_time_ms=500
)
```

#### `save_managers(managers: list[str])`

Сохраняет список менеджеров.

```python
db.save_managers(["Менеджер 1", "Менеджер 2"])
```

#### `get_active_managers() -> list[str]`

Получает активных менеджеров.

```python
managers = db.get_active_managers()
```

#### `add_processing_record(filename, rows_processed, duplicates_removed, processing_time_ms)`

Добавляет запись в историю.

```python
db.add_processing_record(
    filename="file.json",
    rows_processed=100,
    duplicates_removed=10,
    processing_time_ms=500
)
```

#### `get_history(limit: int = 10) -> list[dict]`

Получает историю обработок.

```python
history = db.get_history(limit=10)
```

---

## Миграции

### Версия 1.0 (текущая)

```sql
-- Инициализация базы данных
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    rows_processed INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_statistics_filename ON statistics(filename);
CREATE INDEX IF NOT EXISTS idx_statistics_created_at ON statistics(created_at);

CREATE INDEX IF NOT EXISTS idx_managers_name ON managers(name);
CREATE INDEX IF NOT EXISTS idx_managers_is_active ON managers(is_active);

CREATE INDEX IF NOT EXISTS idx_processing_history_filename ON processing_history(filename);
CREATE INDEX IF NOT EXISTS idx_processing_history_created_at ON processing_history(created_at);
```

### Будущие миграции

#### Версия 2.0 (TODO)

```sql
-- Таблица для настроек пользователя
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для кэша ЛПР
CREATE TABLE IF NOT EXISTS lpr_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    inn TEXT,
    director_name TEXT,
    contacts TEXT,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_lpr_cache_company ON lpr_cache(company_name);
```

---

## Резервное копирование

### Python

```python
import shutil
from pathlib import Path

# Копирование базы данных
db_path = Path("data/database.db")
backup_path = Path("data/backups/database_backup.db")

backup_path.parent.mkdir(exist_ok=True)
shutil.copy2(db_path, backup_path)

print(f"Резервная копия создана: {backup_path}")
```

### SQLite .backup

```python
import sqlite3

# Создание резервной копии через SQLite
conn = sqlite3.connect("data/database.db")
backup_conn = sqlite3.connect("data/backups/database_backup.db")

with backup_conn:
    conn.backup(backup_conn)

backup_conn.close()
conn.close()
```

---

## Запросы для аналитики

### Общая статистика

```sql
-- Всего обработано файлов
SELECT COUNT(*) as total_files FROM statistics;

-- Всего обработано строк
SELECT SUM(rows_processed) as total_rows FROM statistics;

-- Всего удалено дубликатов
SELECT SUM(duplicates_removed) as total_duplicates FROM statistics;

-- Среднее время обработки
SELECT AVG(processing_time_ms) as avg_time_ms FROM statistics;
```

### Статистика по дням

```sql
-- Обработка по дням
SELECT 
    DATE(created_at) as date,
    COUNT(*) as files_count,
    SUM(rows_processed) as rows_total,
    SUM(duplicates_removed) as duplicates_total,
    AVG(processing_time_ms) as avg_time_ms
FROM statistics
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;
```

### Топ файлов по объёму

```sql
-- Топ-10 файлов по количеству строк
SELECT 
    filename,
    rows_processed,
    duplicates_removed,
    processing_time_ms,
    created_at
FROM statistics
ORDER BY rows_processed DESC
LIMIT 10;
```

### Активные менеджеры

```sql
-- Все активные менеджеры
SELECT name, created_at
FROM managers
WHERE is_active = 1
ORDER BY created_at DESC;
```

---

## Производительность

### Оптимизации

- **Индексы** на всех часто используемых колонках
- **Транзакции** для пакетной записи
- **VACUUM** для оптимизации размера БД

### Обслуживание

```sql
-- Оптимизация базы данных
VACUUM;

-- Анализ индексов
ANALYZE;
```

### Рекомендации

1. **Регулярное резервное копирование** (ежедневно)
2. **Очистка старой истории** (>90 дней)
3. **VACUUM** после массового удаления записей

---

## Будущие улучшения

- [ ] Таблица `user_settings` для настроек пользователя
- [ ] Таблица `lpr_cache` для кэширования ЛПР
- [ ] Автоматическое резервное копирование
- [ ] Архивация старой истории
- [ ] Статистика использования по неделям/месяцам

---

**Версия документации:** 1.0  
**Дата обновления:** 20 марта 2026 г.
