# Code Map: Integrations

Карта интеграций приложения LeadGen v5.

**Last Updated:** 2026-03-20
**Версия:** 5.1.0

## Обзор

Приложение интегрируется с внешними сервисами:
- **Битрикс24** — REST API через вебхуки
- **Яндекс.Карты** — генерация ссылок для поиска
- **Webbee AI** — загрузка выгрузок компаний

### Последние изменения (5.1.0)

- **city_timezones.py**: интеграция с генератором ссылок для отображения времени городов

```
modules/
├── bitrix_webhook.py        # REST API Битрикс24
├── bitrix_analytics.py      # Аналитика Битрикс24
└── ...

utils/
├── url_generator.py         # Генератор URL Яндекс.Карт
└── url_cleaner.py           # Очистка URL от UTM
```

---

## Битрикс24

### BitrixWebhookClient

**Расположение:** `modules/bitrix_webhook.py`

**Класс:** `BitrixWebhookClient`

Клиент для работы с REST API Битрикс24 через вебхуки.

#### Инициализация

```python
from modules.bitrix_webhook import BitrixWebhookClient

client = BitrixWebhookClient(
    webhook_url="https://your-company.bitrix24.ru/rest/1/webhook_code/",
    config=config
)
```

#### Методы

##### `test_connection() -> bool`

Проверяет подключение к Битрикс24.

```python
if client.test_connection():
    print("Подключение успешно")
else:
    print("Ошибка подключения")
```

##### `get_new_leads() -> list[dict]`

Получает новые лиды из Битрикс24.

```python
leads = client.get_new_leads()

for lead in leads:
    print(f"Лид: {lead['TITLE']}")
    print(f"Телефон: {lead['PHONE']}")
    print(f"Статус: {lead['STATUS_ID']}")
```

##### `get_managers() -> list[dict]`

Получает список менеджеров (пользователей Битрикс24).

```python
managers = client.get_managers()

for manager in managers:
    print(f"Менеджер: {manager['NAME']} {manager['LAST_NAME']}")
    print(f"Email: {manager['EMAIL']}")
```

##### `assign_lead(lead_id: str, manager_id: str) -> bool`

Назначает лида на менеджера.

```python
success = client.assign_lead(lead_id="123", manager_id="456")

if success:
    print("Лид назначен")
else:
    print("Ошибка назначения")
```

##### `update_lead_status(lead_id: str, status: str) -> bool`

Обновляет статус лида.

```python
success = client.update_lead_status(
    lead_id="123",
    status="В работе"
)
```

##### `get_lead(lead_id: str) -> dict`

Получает лида по ID.

```python
lead = client.get_lead(lead_id="123")
print(f"Название: {lead['TITLE']}")
print(f"Телефон: {lead['PHONE']}")
```

##### `create_lead(fields: dict) -> str`

Создаёт нового лида.

```python
lead_id = client.create_lead(fields={
    "TITLE": "Новый лид",
    "PHONE": "79991234567",
    "STATUS_ID": "Новая заявка",
    "SOURCE_ID": "Холодный звонок"
})

print(f"Лид создан с ID: {lead_id}")
```

##### `make_request(method: str, params: dict = None) -> dict`

Делает произвольный запрос к API Битрикс24.

```python
result = client.make_request(
    method="crm.lead.list",
    params={
        "filter": {"STATUS_ID": "Новая заявка"},
        "select": ["ID", "TITLE", "PHONE"]
    }
)
```

#### Обработка ошибок

```python
from modules.exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookRateLimitError,
    BitrixWebhookConnectionError,
    BitrixWebhookInvalidURLError
)

try:
    leads = client.get_new_leads()
except BitrixWebhookNotFoundError:
    logger.error("Вебхук не найден. Проверьте URL.")
except BitrixWebhookForbiddenError:
    logger.error("Нет прав доступа. Пересоздайте вебхук.")
except BitrixWebhookRateLimitError:
    logger.warning("Превышен лимит запросов. Ждём 1 секунду.")
    time.sleep(1)
except BitrixWebhookConnectionError:
    logger.error("Нет подключения к интернету или Битрикс24 недоступен.")
except BitrixWebhookInvalidURLError:
    logger.error("Неверный формат URL вебхука.")
```

#### Rate Limiting

Битрикс24 ограничивает количество запросов. Клиент автоматически обрабатывает 429 ошибки:

```python
# Внутренняя реализация
def make_request(self, method: str, params: dict = None) -> dict:
    for attempt in range(3):
        try:
            response = requests.post(url, json={...}, timeout=30)
            if response.status_code == 429:
                time.sleep(1)  # Ждём 1 секунду
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt == 2:
                raise BitrixWebhookConnectionError("Таймаут соединения")
```

---

## Битрикс24 Аналитика

### BitrixAnalytics

**Расположение:** `modules/bitrix_analytics.py`

**Класс:** `BitrixAnalytics`

Аналитика из экспорта Битрикс24 (CSV файлы).

#### Инициализация

```python
from modules.bitrix_analytics import BitrixAnalytics

analytics = BitrixAnalytics()
```

#### Методы

##### `load_lead_csv(filepath: str) -> None`

Загружает `LEAD.csv` из экспорта Битрикс24.

```python
analytics.load_lead_csv("LEAD.csv")
```

##### `load_deal_csv(filepath: str) -> None`

Загружает `DEAL.csv` из экспорта Битрикс24.

```python
analytics.load_deal_csv("DEAL.csv")
```

##### `build_funnel() -> dict`

Строит воронку продаж.

```python
funnel = analytics.build_funnel()

print(f"Новая заявка: {funnel['Новая заявка']}")
print(f"В работе: {funnel['В работе']}")
print(f"Успешно: {funnel['Успешно']}")
```

##### `group_by_manager() -> DataFrame`

Группирует по менеджерам.

```python
by_manager = analytics.group_by_manager()

for _, row in by_manager.iterrows():
    print(f"{row['manager']}: {row['leads']} лидов")
```

##### `group_by_category() -> DataFrame`

Группирует по категориям.

```python
by_category = analytics.group_by_category()

for _, row in by_category.iterrows():
    print(f"{row['category']}: {row['count']} компаний")
```

##### `group_by_source() -> DataFrame`

Группирует по источникам.

```python
by_source = analytics.group_by_source()

for _, row in by_source.iterrows():
    print(f"{row['source']}: {row['leads']} лидов")
```

##### `get_rejection_reasons() -> DataFrame`

Получает причины отказа.

```python
reasons = analytics.get_rejection_reasons()

for _, row in reasons.iterrows():
    print(f"{row['reason']}: {row['count']}")
```

---

## Яндекс.Карты

### URL Generator

**Расположение:** `utils/url_generator.py`

**Функция:** `generate_yandex_maps_url()`

Генератор URL для поиска на Яндекс.Картах.

#### Пример использования

```python
from utils.url_generator import generate_yandex_maps_url

# Простой запрос
url = generate_yandex_maps_url(
    query="Рестораны",
    city="Москва"
)
# https://yandex.ru/maps/?text=Рестораны+Москва

# С районом
url = generate_yandex_maps_url(
    query="Кофейни",
    city="Санкт-Петербург",
    district="Центральный район"
)
# https://yandex.ru/maps/?text=Кофейни+Санкт-Петербург+Центральный+район
```

#### Параметры

```python
def generate_yandex_maps_url(
    query: str,           # Поисковый запрос
    city: str,            # Город
    district: str = None, # Район (опционально)
) -> str
```

---

## Очистка URL

### URL Cleaner

**Расположение:** `utils/url_cleaner.py`

**Функция:** `clean_url()`

Очистка URL от UTM-меток и лишних параметров.

#### Пример использования

```python
from utils.url_cleaner import clean_url

# Очистка от UTM-меток
clean = clean_url("https://example.com?utm_source=google&utm_campaign=test")
# "https://example.com"

# Сохранение важных параметров
clean = clean_url("https://example.com?page=1&utm_source=google")
# "https://example.com?page=1"
```

#### Параметры

```python
def clean_url(
    url: str,
    keep_params: list[str] = None,  # Параметры для сохранения
) -> str
```

---

## Webbee AI

### Загрузка выгрузок

**Расположение:** `modules/data_processor.py`

**Функция:** `load_file()`

Загрузка выгрузок от Webbee AI (JSON/TSV/CSV).

#### Пример использования

```python
from modules.data_processor import load_file

# Загрузка JSON
df = load_file("webbee_export.json")

# Загрузка TSV
df = load_file("webbee_export.tsv")

# Загрузка CSV
df = load_file("webbee_export.csv")
```

#### Формат данных Webbee AI

```json
{
    "items": [
        {
            "name": "Компания 1",
            "phone": "7.8005001695e+10",
            "address": "Москва, ул. Примерная, 1",
            "website": "https://example.com",
            "category": "Рестораны"
        }
    ]
}
```

---

## Взаимодействие между модулями

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer                            │
│  (gui/pages/*)                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│              Service Layer                              │
│  (ProcessingService, DependencyContainer)               │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        v                   v                   v
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Bitrix       │   │ Data         │   │ Utils        │
│ Webhook      │   │ Processor    │   │ (url_*)      │
│              │   │              │   │              │
│ - get_leads  │   │ - load_file  │   │ - generate_  │
│ - assign     │   │ - merge      │   │   yandex_url │
│ - analytics  │   │ - clean      │   │ - clean_url  │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## Тестирование

### Тесты BitrixWebhookClient

```python
# tests/test_bitrix_webhook.py
import pytest
from unittest.mock import Mock, patch
from modules.bitrix_webhook import BitrixWebhookClient

@pytest.fixture
def mock_config():
    return {"bitrix": {"stage": "Новая заявка"}}

def test_get_new_leads_success(mock_config):
    client = BitrixWebhookClient("https://test.bitrix24.ru/rest/1/code/", mock_config)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "result": [
                {"ID": "1", "TITLE": "Лид 1", "PHONE": "79991234567"}
            ]
        }
        
        leads = client.get_new_leads()
        
        assert len(leads) == 1
        assert leads[0]["TITLE"] == "Лид 1"

def test_get_new_leads_not_found(mock_config):
    client = BitrixWebhookClient("https://test.bitrix24.ru/rest/1/code/", mock_config)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 404
        
        with pytest.raises(BitrixWebhookNotFoundError):
            client.get_new_leads()
```

### Тесты URL Generator

```python
# tests/test_url_generator.py
from utils.url_generator import generate_yandex_maps_url

def test_generate_url_simple():
    url = generate_yandex_maps_url(
        query="Рестораны",
        city="Москва"
    )
    assert "Рестораны" in url
    assert "Москва" in url

def test_generate_url_with_district():
    url = generate_yandex_maps_url(
        query="Кофейни",
        city="Санкт-Петербург",
        district="Центральный район"
    )
    assert "Кофейни" in url
    assert "Санкт-Петербург" in url
    assert "Центральный район" in url
```

### Тесты URL Cleaner

```python
# tests/test_url_cleaner.py
from utils.url_cleaner import clean_url

def test_clean_url_remove_utm():
    clean = clean_url("https://example.com?utm_source=google&utm_campaign=test")
    assert clean == "https://example.com"

def test_clean_url_keep_params():
    clean = clean_url(
        "https://example.com?page=1&utm_source=google",
        keep_params=["page"]
    )
    assert "page=1" in clean
    assert "utm_source" not in clean
```

---

## Безопасность

### Вебхуки Битрикс24

**Правила безопасности:**

1. **НЕ хранить** вебхук в `config.json`
2. Использовать переменные окружения (`.env`)
3. Ограничивать права вебхука (только crm, user)
4. Регулярно обновлять вебхук

```env
# .env
BITRIX_WEBHOOK_URL=https://your-company.bitrix24.ru/rest/1/webhook_code/
```

### Валидация URL

```python
from modules.exceptions import BitrixWebhookInvalidURLError

def validate_webhook_url(url: str) -> bool:
    if not url:
        return False
    
    # Проверка формата Битрикс24
    if not url.startswith("https://") or ".bitrix24" not in url:
        raise BitrixWebhookInvalidURLError("Неверный формат URL")
    
    return True
```

---

## Производительность

### Оптимизации

- **Кэширование ответов Битрикс24** (TODO)
- **Пакетные запросы** к API
- **Rate limiting** с экспоненциальной задержкой

### Проблемы

- API Битрикс24 может быть медленным при больших объёмах данных
- Решение: фоновая загрузка (TODO)

---

## Будущие улучшения

- [ ] Интеграция с amoCRM
- [ ] Поддержка множественных порталов Битрикс24
- [ ] Вебхуки для входящих событий
- [ ] Синхронизация в реальном времени
- [ ] Интеграция с Telegram для уведомлений
