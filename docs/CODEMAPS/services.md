# Code Map: Services

Карта сервисов приложения LeadGen v5.

## Обзор

Сервисный слой расположен в `modules/services/` и `core/`. Он предоставляет абстракцию между GUI и бизнес-логикой, упрощает тестирование и уменьшает связанность компонентов.

```
core/
└── dependency_container.py    # Контейнер зависимостей

modules/services/
└── processing_service.py      # Сервис обработки лидов
```

---

## DependencyContainer

### Расположение

`core/dependency_container.py`

### Назначение

Централизованное управление зависимостями для упрощения тестирования и уменьшения связанности компонентов.

### Класс `DependencyContainer`

```python
class DependencyContainer:
    """
    Контейнер зависимостей приложения.
    
    Предоставляет централизованное создание и управление сервисами.
    Реализует ленивую инициализацию (создание по требованию).
    """
    
    def __init__(self, config: dict | None = None)
    
    @property
    def config(self) -> dict
        """Возвращает конфигурацию приложения."""
    
    def get_db_manager(self) -> DatabaseManager
        """Возвращает менеджер базы данных."""
    
    def get_processing_service(self) -> ProcessingService
        """Возвращает сервис обработки данных."""
    
    def get_bitrix_client(self) -> BitrixWebhookClient
        """Возвращает клиент для работы с API Битрикс24."""
```

### Ленивая инициализация

Сервисы создаются только при первом вызове соответствующего метода:

```python
container = DependencyContainer()

# В этот момент сервисы ещё не созданы
# ...

# При первом вызове сервис создаётся и кэшируется
processing_service = container.get_processing_service()

# При повторном вызове возвращается тот же экземпляр
same_service = container.get_processing_service()
assert processing_service is same_service  # True
```

### Пример использования

```python
from core.dependency_container import DependencyContainer

# Инициализация контейнера
container = DependencyContainer()

# Получение сервисов
processing_service = container.get_processing_service()
bitrix_client = container.get_bitrix_client()
db_manager = container.get_db_manager()

# Обработка файлов
df, stats = processing_service.process_files(
    file_paths=["file1.json", "file2.json"],
    managers=["Менеджер 1", "Менеджер 2"]
)

# Экспорт в CSV
output_path = processing_service.export_to_csv(df, "output.csv")

# Работа с Битрикс24
if bitrix_client.test_connection():
    leads = bitrix_client.get_new_leads()
```

### Тестирование с моками

```python
# tests/test_processing_service.py
import pytest
from unittest.mock import Mock
from modules.services.processing_service import ProcessingService

@pytest.fixture
def mock_db_manager():
    return Mock()

@pytest.fixture
def mock_config():
    return {
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

def test_process_files(mock_db_manager, mock_config):
    service = ProcessingService(mock_db_manager, mock_config)
    df, stats = service.process_files(["test.json"], ["Manager 1"])
    
    assert not df.empty
    assert stats["rows_processed"] > 0
    mock_db_manager.add_processing_record.assert_called_once()
```

---

## ProcessingService

### Расположение

`modules/services/processing_service.py`

### Назначение

Сервис для обработки лидов. Предоставляет абстракцию между GUI и бизнес-логикой.

### Класс `ProcessingService`

```python
class ProcessingService:
    """
    Сервис для обработки лидов.
    
    Example:
        >>> db_manager = DatabaseManager("data/database.db")
        >>> service = ProcessingService(db_manager, config)
        >>> df, stats = service.process_files(["file1.json"], ["Manager 1"])
    """
    
    def __init__(
        self,
        db_manager: IDatabaseManager,
        config: dict,
    )
    
    def process_files(
        self,
        file_paths: list[str],
        managers: list[str],
    ) -> tuple[pd.DataFrame, dict]
        """
        Обрабатывает файлы и возвращает результат для Битрикс24.
        
        Args:
            file_paths: Список путей к файлам
            managers: Список имён менеджеров
        
        Returns:
            Кортеж (DataFrame для Битрикс, статистика)
        
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если данные невалидны
        """
    
    def export_to_csv(
        self,
        df: pd.DataFrame,
        filepath: str,
    ) -> str
        """
        Экспортирует DataFrame в CSV файл.
        
        Args:
            df: DataFrame с данными
            filepath: Путь для сохранения файла
        
        Returns:
            Путь к сохранённому файлу
        
        Raises:
            IOError: Если не удалось сохранить файл
        """
```

### Внутренние методы

```python
def _validate_files(self, file_paths: list[str]) -> None:
    """Проверяет существование файлов."""

def _save_to_database(self, file_paths: list[str], stats: dict) -> None:
    """Сохраняет статистику обработки в БД."""
```

### Протокол IDatabaseManager

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class IDatabaseManager(Protocol):
    """Протокол для менеджера базы данных."""
    
    def add_processing_record(
        self,
        filename: str,
        rows_processed: int,
        duplicates_removed: int,
        processing_time_ms: int,
    ) -> None: ...
```

Это позволяет использовать моки для тестирования.

### Поток данных

```
1. process_files() вызывается с file_paths и managers
         │
         v
2. _validate_files() проверяет существование файлов
         │
         v
3. merge_files() обрабатывает файлы (data_processor)
         │
         v
4. map_to_bitrix() маппит данные (bitrix_mapper)
         │
         v
5. _save_to_database() сохраняет статистику
         │
         v
6. Возврат (DataFrame, stats)
```

### Пример использования

```python
from modules.services.processing_service import ProcessingService
from database.db_manager import DatabaseManager

# Инициализация
db_manager = DatabaseManager("data/database.db")
service = ProcessingService(db_manager, config)

# Обработка файлов
try:
    df_bitrix, stats = service.process_files(
        file_paths=["file1.json", "file2.json"],
        managers=["Елена Юматова", "Менеджер 2"]
    )
    
    print(f"Обработано строк: {stats['rows_processed']}")
    print(f"Удалено дубликатов: {stats['duplicates_removed']}")
    print(f"Время обработки: {stats['processing_time_ms']} мс")
    
    # Экспорт в CSV
    output_path = service.export_to_csv(df_bitrix, "output.csv")
    print(f"Файл сохранён: {output_path}")
    
except FileNotFoundError as e:
    print(f"Файл не найден: {e}")
except ValueError as e:
    print(f"Ошибка валидации: {e}")
except IOError as e:
    print(f"Ошибка экспорта: {e}")
```

### Обработка ошибок

```python
from modules.exceptions import (
    ProcessingError,
    ValidationError,
    ExportError
)

try:
    df, stats = service.process_files(["file.json"], ["Manager 1"])
except ProcessingError as e:
    logger.error(f"Ошибка обработки: {e}")
except ValidationError as e:
    logger.error(f"Ошибка валидации: {e}")
except ExportError as e:
    logger.error(f"Ошибка экспорта: {e}")
```

---

## Взаимодействие между сервисами

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer                            │
│  (gui/pages/processing_page.py)                         │
└─────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│              DependencyContainer                        │
│  (core/dependency_container.py)                         │
│                                                         │
│  - get_processing_service()                             │
│  - get_bitrix_client()                                  │
│  - get_db_manager()                                     │
└─────────────────────────────────────────────────────────┘
        │                   │                   │
        v                   v                   v
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Processing   │   │ Bitrix       │   │ Database     │
│ Service      │   │ Webhook      │   │ Manager      │
│              │   │ Client       │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
        │
        v
┌─────────────────────────────────────────────────────────┐
│              Business Logic Layer                       │
│  (modules/data_processor.py, modules/bitrix_mapper.py)  │
└─────────────────────────────────────────────────────────┘
```

---

## Расширение

### Добавление нового сервиса

1. Создать файл `modules/services/new_service.py`:

```python
"""Новый сервис."""

import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class INewServiceDependency(Protocol):
    """Протокол для зависимости нового сервиса."""
    
    def some_method(self, arg: str) -> str: ...


class NewService:
    """
    Новый сервис.
    
    Example:
        >>> dependency = SomeDependency()
        >>> service = NewService(dependency, config)
        >>> result = service.do_something("data")
    """
    
    def __init__(
        self,
        dependency: INewServiceDependency,
        config: dict,
    ):
        """
        Инициализирует сервис.
        
        Args:
            dependency: Зависимость сервиса
            config: Конфигурация приложения
        """
        self._dependency = dependency
        self._config = config
    
    def do_something(self, data: str) -> str:
        """
        Выполняет действие.
        
        Args:
            data: Входные данные
        
        Returns:
            Результат выполнения
        
        Raises:
            ValueError: Если данные невалидны
        """
        logger.info(f"Выполняется действие над: {data}")
        return data.upper()
```

2. Добавить в `DependencyContainer`:

```python
# core/dependency_container.py
from modules.services.new_service import NewService

class DependencyContainer:
    def __init__(self, config: dict | None = None):
        # ...
        self._new_service: NewService | None = None
    
    def get_new_service(self) -> NewService:
        """Возвращает новый сервис."""
        if self._new_service is None:
            dependency = self.get_some_dependency()
            self._new_service = NewService(
                dependency=dependency,
                config=self._config
            )
            logger.debug("NewService создан")
        return self._new_service
```

3. Написать тесты в `tests/test_new_service.py`

---

## Тестирование

### Тесты ProcessingService

```python
# tests/test_processing_service.py
import pytest
from unittest.mock import Mock, patch
from modules.services.processing_service import ProcessingService

@pytest.fixture
def mock_db_manager():
    db = Mock()
    db.add_processing_record = Mock()
    return db

@pytest.fixture
def mock_config():
    return {
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

def test_process_files_success(mock_db_manager, mock_config):
    """Тест успешной обработки файлов."""
    service = ProcessingService(mock_db_manager, mock_config)
    
    with patch('modules.services.processing_service.merge_files') as mock_merge:
        mock_merge.return_value = (Mock(empty=False), {"rows_processed": 100})
        
        with patch('modules.services.processing_service.map_to_bitrix') as mock_map:
            mock_map.return_value = Mock()
            
            df, stats = service.process_files(["test.json"], ["Manager 1"])
            
            assert stats["rows_processed"] == 100
            mock_db_manager.add_processing_record.assert_called_once()

def test_process_files_empty_managers(mock_db_manager, mock_config):
    """Тест с пустым списком менеджеров."""
    service = ProcessingService(mock_db_manager, mock_config)
    
    with pytest.raises(ValueError, match="Список менеджеров не может быть пустым"):
        service.process_files(["test.json"], [])

def test_process_files_not_found(mock_db_manager, mock_config):
    """Тест с несуществующим файлом."""
    service = ProcessingService(mock_db_manager, mock_config)
    
    with pytest.raises(FileNotFoundError):
        service.process_files(["nonexistent.json"], ["Manager 1"])
```

---

## Производительность

### Оптимизации

- **Ленивая инициализация:** сервисы создаются только при необходимости
- **Кэширование экземпляров:** один экземпляр сервиса на всё приложение
- **Пакетная запись в БД:** транзакции для уменьшения количества операций

### Проблемы

- Обработка больших файлов (>10000 строк) может занимать несколько минут
- Решение: асинхронная обработка (TODO)

---

## Будущие улучшения

- [ ] Асинхронная обработка файлов
- [ ] Поддержка очередей задач (Celery)
- [ ] Распределённая обработка
- [ ] Кэширование результатов маппинга
- [ ] Стриминговая обработка больших файлов
