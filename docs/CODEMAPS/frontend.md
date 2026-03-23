# Code Map: Frontend (GUI)

Карта frontend модулей приложения LeadGen v5.

**Last Updated:** 2026-03-20
**Версия:** 5.1.0

## Обзор

Frontend приложение построено на **PySide6** (Qt для Python) и следует архитектуре MVVM с разделением на страницы, компоненты и утилиты.

### Последние изменения (5.1.0)

- **Генератор ссылок**: новая компоновка (сегмент+результаты слева, города справа)
- **Часовые пояса**: функция `get_city_timezone()` в утилитах
- **Диалог управления городами**: модальное окно для редактирования списка городов
- **HomePage**: добавлен логотип приложения
- **Glassmorphism стили**: новые переменные темы (`GLASS_CARD_BG`, `GLASS_BORDER`, etc.)
- **Удалено**: управление городами из настроек, дублирование кнопок "Добавить город"

```
gui/
├── main_window.py          # Главное окно приложения
├── sidebar.py              # Боковая навигационная панель
├── preview_table.py        # Таблица предпросмотра данных
├── progress_bar.py         # Виджет прогресс-бара
│
├── pages/                  # Страницы приложения
│   ├── home_page.py        # Главная страница
│   ├── processing_page.py  # Обработка файлов
│   ├── analytics_page.py   # Аналитика Битрикс
│   ├── link_generator_page.py  # Генератор ссылок
│   ├── lpr_finder_page.py  # Поиск ЛПР
│   ├── manager_monitor_page.py  # Мониторинг менеджеров
│   └── settings_page.py    # Настройки
│
├── components/             # Переиспользуемые компоненты
│   ├── circular_progress.py
│   ├── file_list.py
│   └── file_loader.py
│
├── styles/                 # Стили и темы
│   ├── stylesheet.py       # Таблицы стилей
│   └── theme.py            # Цветовые переменные
│
├── threads/                # Фоновые потоки
│   └── processing_thread.py
│
└── utils/                  # Утилиты GUI
    ├── error_handler.py
    └── thread_helpers.py
```

---

## Точки входа

### main_window.py

**Класс:** `MainWindow`

Главное окно приложения с sidebar навигацией и QStackedWidget для переключения страниц.

```python
from gui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

**Зависимости:**
- `gui.sidebar.Sidebar`
- `gui.pages.*` (все страницы)
- `gui.styles.stylesheet`
- `gui.styles.theme`

---

## Страницы (gui/pages/)

### home_page.py

**Класс:** `HomePage`

Главная страница с быстрыми переходами к основным функциям.

**Компоненты (5.1.0):**
- **Логотип приложения**: визуальный элемент в приветственной секции
- Карточки быстрых действий с glassmorphism эффектами
- Обновлённая типографика (шрифты, отступы)

**Изменения в 5.1.0:**
- Добавлен виджет логотипа
- Применены glassmorphism стили (`GLASS_CARD_BG`, `GLASS_BUTTON_BG`)
- Улучшена структура приветственной секции

**Сигналы:**
- `navigate_to(page_index: int)` — переход на страницу

### processing_page.py

**Класс:** `ProcessingPage`

Страница обработки файлов Webbee AI.

**Компоненты:**
- `FileLoader` — загрузка файлов (Drag & Drop)
- `FileList` — список загруженных файлов
- `CircularProgress` — индикатор обработки
- `PreviewTable` — предпросмотр данных

**Сигналы:**
- `files_loaded(file_paths: list[str])`
- `processing_started()`
- `processing_finished(stats: dict)`
- `error_occurred(error: str)`

**Слоты:**
- `handle_load_files()` — обработка загрузки
- `handle_process()` — запуск обработки
- `handle_export()` — экспорт в CSV

### analytics_page.py

**Класс:** `AnalyticsPage`

Страница аналитики Битрикс24.

**Компоненты:**
- Загрузчик CSV файлов
- Вкладки аналитики (воронки, менеджеры, категории)
- Графики (matplotlib)

**Сигналы:**
- `analysis_started()`
- `analysis_finished(results: dict)`

### link_generator_page.py

**Класс:** `LinkGeneratorPage`

Генератор ссылок Яндекс.Карт.

**Компоненты (5.1.0):**
- `QSplitter` — разделение на левую/правую панель
- Левая панель: поле ввода сегмента, таблица результатов, кнопки действий
- Правая панель: scrollable список городов с чекбоксами
- **Диалог управления городами**: модальное окно для добавления/удаления городов и районов
- **Часовые пояса**: отображение времени для каждого города

**Изменения в 5.1.0:**
- Новая компоновка: сегмент+результаты слева, города справа (было: сверху)
- Удалено управление городами из настроек (перемещено в диалог)
- Удалено дублирование кнопок "Добавить город"
- Добавлено сохранение выбранных городов между сессиями

**Сигналы:**
- `links_generated(count: int)` — количество сгенерированных ссылок

### lpr_finder_page.py

**Класс:** `LPRFinderPage`

Поиск ЛПР (лицо, принимающее решение).

**Компоненты:**
- Загрузчик CSV компаний
- Таблица результатов парсинга

### manager_monitor_page.py

**Класс:** `ManagerMonitorPage`

Мониторинг менеджеров в реальном времени.

**Компоненты:**
- Таблица распределения лидов
- Исключение менеджеров

### settings_page.py

**Класс:** `SettingsPage`

Настройки приложения.

**Компоненты:**
- Настройки обработки телефонов
- Настройки путей
- Настройки UI
- Настройки Битрикс24

---

## Компоненты (gui/components/)

### circular_progress.py

**Класс:** `CircularProgress`

Круговой индикатор прогресса.

**Свойства:**
- `value: int` — текущее значение (0-100)
- `maximum: int` — максимальное значение
- `color: QColor` — цвет прогресса

### file_list.py

**Класс:** `FileList`

Список загруженных файлов.

**Методы:**
- `add_file(path: str)` — добавить файл
- `remove_file(index: int)` — удалить файл
- `get_files() -> list[str]` — получить все файлы

### file_loader.py

**Класс:** `FileLoader`

Загрузка файлов через Drag & Drop.

**Сигналы:**
- `files_dropped(paths: list[str])`

**Методы:**
- `open_file_dialog() -> list[str]` — диалог выбора файлов

---

## Стили (gui/styles/)

### theme.py

Цветовые переменные для тёмной темы:

```python
# Основные цвета
BACKGROUND_PRIMARY = "#1e1e1e"
BACKGROUND_SECONDARY = "#252525"
BACKGROUND_TERTIARY = "#2d2d2d"
ACCENT_CYAN = "#00bcd4"
ACCENT_GREEN = "#4caf50"
ACCENT_RED = "#f44336"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"

# Glassmorphism (5.1.0)
GLASS_CARD_BG = "rgba(45, 45, 45, 0.6)"
GLASS_BORDER = "rgba(255, 255, 255, 0.1)"
GLASS_BUTTON_BG = "rgba(0, 188, 212, 0.2)"
GLASS_HOVER = "rgba(0, 188, 212, 0.3)"
```

### stylesheet.py

Таблицы стилей для виджетов:

- `MAIN_WINDOW_STYLES` — стили главного окна
- `SIDEBAR_STYLES` — стили sidebar
- `BUTTON_STYLES` — стили кнопок
- `TABLE_STYLES` — стили таблиц
- `INPUT_STYLES` — стили полей ввода
- `GLASS_CARD_STYLES` — стили glassmorphism карточек (5.1.0)

---

## Потоки (gui/threads/)

### processing_thread.py

**Класс:** `ProcessingThread`

Фоновый поток обработки файлов.

**Сигналы:**
- `progress(value: int)` — прогресс обработки
- `finished(result: DataFrame, stats: dict)` — завершение
- `error(message: str)` — ошибка

**Класс:** `ExportThread`

Фоновый поток экспорта в CSV.

---

## Утилиты (gui/utils/)

### error_handler.py

Обработка ошибок GUI:

```python
from gui.utils.error_handler import show_error, show_warning

show_error("Ошибка обработки файла")
show_warning("Файл не найден")
```

### thread_helpers.py

**Класс:** `ThreadCleanupMixin`

Миксин для безопасной очистки потоков.

---

## Взаимодействие между модулями

```
┌─────────────────┐
│   MainWindow    │
│                 │
│  ┌───────────┐  │
│  │  Sidebar  │  │
│  └───────────┘  │
│        │        │
│        v        │
│  ┌───────────┐  │
│  │QStackedWidget││
│  │  Pages    │  │
│  └───────────┘  │
└─────────────────┘
        │
        v
┌─────────────────┐
│ProcessingService│ ← DependencyContainer
└─────────────────┘
        │
        v
┌─────────────────┐
│  Business Logic │
│   (modules/)    │
└─────────────────┘
```

---

## Событийный цикл

1. **Инициализация:**
   - `QApplication` создаётся в `main.py`
   - `MainWindow` инициализируется
   - Загружается `config.json`
   - Инициализируется `DependencyContainer`

2. **Загрузка файлов:**
   - Пользователь перетаскивает файлы в `FileLoader`
   - `FileLoader` отправляет сигнал `files_dropped`
   - `ProcessingPage` получает файлы
   - Отображает в `FileList`

3. **Обработка:**
   - Пользователь нажимает «Обработать»
   - `ProcessingPage` создаёт `ProcessingThread`
   - Поток вызывает `ProcessingService.process_files()`
   - Прогресс обновляется через сигнал `progress`
   - Результат отображается в `PreviewTable`

4. **Экспорт:**
   - Пользователь нажимает «Экспортировать»
   - `ExportThread` вызывает `export_to_bitrix_csv()`
   - Файл сохраняется

---

## Расширение

### Добавление новой страницы

1. Создать файл `gui/pages/new_page.py`:

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

2. Добавить импорт в `gui/main_window.py`:

```python
from gui.pages.new_page import NewPage
```

3. Добавить страницу в `QStackedWidget`:

```python
self.stack.addWidget(NewPage())
```

4. Добавить кнопку в `gui/sidebar.py`

---

## Тестирование

### GUI тесты

```python
# tests/test_gui/test_main_window.py
import pytest
from gui.main_window import MainWindow

def test_main_window_creation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "LeadGen v5"
```

### Тесты компонентов

```python
# tests/test_gui/test_file_loader.py
def test_file_loader_drag_drop(qtbot, tmp_path):
    loader = FileLoader()
    # Тест Drag & Drop
```

---

## Производительность

### Оптимизации

- **Пагинация таблиц:** отображение максимум 100 строк
- **Фоновые потоки:** обработка не блокирует UI
- **Ленивая загрузка:** страницы создаются по требованию

### Проблемы

- Большие файлы (>10000 строк) могут замедлять предпросмотр
- Решение: виртуализация таблиц (TODO)

---

## Будущие улучшения

- [ ] Виртуализация таблиц для больших данных
- [ ] Поддержка светлой темы
- [ ] Анимации переходов между страницами
- [ ] Горячие клавиши
- [ ] Система уведомлений
