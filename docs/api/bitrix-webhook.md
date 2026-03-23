# BitrixWebhookClient API

Документация по клиенту REST API Битрикс24.

## Обзор

`BitrixWebhookClient` предоставляет Python-интерфейс для работы с REST API Битрикс24 через вебхуки.

**Расположение:** `modules/bitrix_webhook.py`

---

## Быстрый старт

### Инициализация

```python
from modules.bitrix_webhook import BitrixWebhookClient

client = BitrixWebhookClient(
    webhook_url="https://your-company.bitrix24.ru/rest/1/webhook_code/",
    config=config
)
```

### Проверка подключения

```python
if client.test_connection():
    print("✓ Подключение к Битрикс24 успешно")
else:
    print("✗ Ошибка подключения")
```

---

## Работа с лидами

### Получение новых лидов

```python
leads = client.get_new_leads()

for lead in leads:
    print(f"ID: {lead['ID']}")
    print(f"Название: {lead['TITLE']}")
    print(f"Телефон: {lead['PHONE']}")
    print(f"Статус: {lead['STATUS_ID']}")
    print("---")
```

**Возвращает:** `list[dict]` — список лидов

### Получение лида по ID

```python
lead = client.get_lead(lead_id="123")

print(f"Название: {lead['TITLE']}")
print(f"Описание: {lead['COMMENTS']}")
```

**Параметры:**
- `lead_id` (str) — ID лида

**Возвращает:** `dict` — данные лида

### Создание лида

```python
lead_id = client.create_lead(fields={
    "TITLE": "Новый лид из приложения",
    "PHONE": "79991234567",
    "EMAIL": "client@example.com",
    "STATUS_ID": "Новая заявка",
    "SOURCE_ID": "Холодный звонок",
    "COMMENTS": "Интересуется услугами компании"
})

print(f"Лид создан с ID: {lead_id}")
```

**Параметры:**
- `fields` (dict) — поля лида

**Возвращает:** `str` — ID созданного лида

**Поля лида:**

| Поле | Тип | Описание |
|------|-----|----------|
| TITLE | str | Название лида |
| NAME | str | Имя контакта |
| SECOND_NAME | str | Отчество контакта |
| LAST_NAME | str | Фамилия контакта |
| PHONE | str | Телефон |
| EMAIL | str | Email |
| STATUS_ID | str | ID статуса |
| SOURCE_ID | str | ID источника |
| COMMENTS | str | Комментарий |
| COMPANY_TITLE | str | Название компании |
| COMPANY_WEB | str | Сайт компании |
| COMPANY_ADDRESS | str | Адрес компании |

### Обновление лида

```python
success = client.update_lead(
    lead_id="123",
    fields={
        "STATUS_ID": "В работе",
        "COMMENTS": "Обновлённый комментарий"
    }
)

if success:
    print("Лид обновлён")
```

**Параметры:**
- `lead_id` (str) — ID лида
- `fields` (dict) — поля для обновления

**Возвращает:** `bool` — успех операции

### Обновление статуса лида

```python
success = client.update_lead_status(
    lead_id="123",
    status="В работе"
)
```

**Параметры:**
- `lead_id` (str) — ID лида
- `status` (str) — новый статус

**Возвращает:** `bool` — успех операции

### Удаление лида

```python
success = client.delete_lead(lead_id="123")

if success:
    print("Лид удалён")
```

**Параметры:**
- `lead_id` (str) — ID лида

**Возвращает:** `bool` — успех операции

---

## Работа с менеджерами

### Получение списка менеджеров

```python
managers = client.get_managers()

for manager in managers:
    print(f"ID: {manager['ID']}")
    print(f"Имя: {manager['NAME']} {manager['LAST_NAME']}")
    print(f"Email: {manager['EMAIL']}")
    print(f"Активен: {manager['ACTIVE']}")
    print("---")
```

**Возвращает:** `list[dict]` — список менеджеров

**Поля менеджера:**

| Поле | Тип | Описание |
|------|-----|----------|
| ID | str | ID пользователя |
| NAME | str | Имя |
| LAST_NAME | str | Фамилия |
| EMAIL | str | Email |
| ACTIVE | bool | Активен ли |
| PERSONAL_PHONE | str | Личный телефон |
| WORK_PHONE | str | Рабочий телефон |

### Назначение лида на менеджера

```python
success = client.assign_lead(
    lead_id="123",
    manager_id="456"
)

if success:
    print("Лид назначен на менеджера")
```

**Параметры:**
- `lead_id` (str) — ID лида
- `manager_id` (str) — ID менеджера

**Возвращает:** `bool` — успех операции

### Получение лидов по менеджеру

```python
leads = client.get_leads_by_manager(manager_id="456")

print(f"У менеджера {len(leads)} лидов")
```

**Параметры:**
- `manager_id` (str) — ID менеджера

**Возвращает:** `list[dict]` — список лидов

---

## Работа со сделками

### Получение сделок

```python
deals = client.get_deals()

for deal in deals:
    print(f"ID: {deal['ID']}")
    print(f"Название: {deal['TITLE']}")
    print(f"Сумма: {deal['OPPORTUNITY']}")
    print(f"Стадия: {deal['STAGE_ID']}")
    print("---")
```

**Возвращает:** `list[dict]` — список сделок

### Получение сделки по ID

```python
deal = client.get_deal(deal_id="123")
```

**Параметры:**
- `deal_id` (str) — ID сделки

**Возвращает:** `dict` — данные сделки

### Создание сделки

```python
deal_id = client.create_deal(fields={
    "TITLE": "Сделка с клиентом",
    "OPPORTUNITY": "100000",
    "STAGE_ID": "NEW",
    "COMMENTS": "Новая сделка"
})
```

**Параметры:**
- `fields` (dict) — поля сделки

**Возвращает:** `str` — ID созданной сделки

---

## Работа с компаниями

### Получение компаний

```python
companies = client.get_companies()

for company in companies:
    print(f"ID: {company['ID']}")
    print(f"Название: {company['TITLE']}")
    print(f"Сайт: {company['WEB']}")
    print(f"Адрес: {company['ADDRESS']}")
    print("---")
```

**Возвращает:** `list[dict]` — список компаний

### Получение компании по ID

```python
company = client.get_company(company_id="123")
```

**Параметры:**
- `company_id` (str) — ID компании

**Возвращает:** `dict` — данные компании

---

## Произвольные запросы

### make_request

Метод для выполнения произвольных запросов к API Битрикс24.

```python
# Получение списка лидов с фильтрацией
result = client.make_request(
    method="crm.lead.list",
    params={
        "filter": {"STATUS_ID": "Новая заявка"},
        "select": ["ID", "TITLE", "PHONE", "EMAIL"]
    }
)

print(f"Найдено лидов: {len(result.get('result', []))}")
```

**Параметры:**
- `method` (str) — метод API (например, `crm.lead.list`)
- `params` (dict, optional) — параметры запроса

**Возвращает:** `dict` — ответ API

### Методы API Битрикс24

#### Лиды (crm.lead)

| Метод | Описание |
|-------|----------|
| `crm.lead.list` | Список лидов |
| `crm.lead.get` | Получение лида |
| `crm.lead.add` | Создание лида |
| `crm.lead.update` | Обновление лида |
| `crm.lead.delete` | Удаление лида |
| `crm.lead.fields` | Поля лида |

#### Сделки (crm.deal)

| Метод | Описание |
|-------|----------|
| `crm.deal.list` | Список сделок |
| `crm.deal.get` | Получение сделки |
| `crm.deal.add` | Создание сделки |
| `crm.deal.update` | Обновление сделки |
| `crm.deal.delete` | Удаление сделки |

#### Компании (crm.company)

| Метод | Описание |
|-------|----------|
| `crm.company.list` | Список компаний |
| `crm.company.get` | Получение компании |
| `crm.company.add` | Создание компании |
| `crm.company.update` | Обновление компании |
| `crm.company.delete` | Удаление компании |

#### Контакты (crm.contact)

| Метод | Описание |
|-------|----------|
| `crm.contact.list` | Список контактов |
| `crm.contact.get` | Получение контакта |
| `crm.contact.add` | Создание контакта |
| `crm.contact.update` | Обновление контакта |
| `crm.contact.delete` | Удаление контакта |

#### Пользователи (user)

| Метод | Описание |
|-------|----------|
| `user.list` | Список пользователей |
| `user.get` | Получение пользователя |

---

## Обработка ошибок

### Иерархия исключений

```
BitrixWebhookError (базовое)
├── BitrixWebhookNotFoundError (404)
├── BitrixWebhookForbiddenError (403)
├── BitrixWebhookRateLimitError (429)
├── BitrixWebhookInvalidURLError
└── BitrixWebhookConnectionError
```

### Пример обработки

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
    logger.error("Вебхук не найден. Проверьте URL вебхука.")
except BitrixWebhookForbiddenError:
    logger.error("Нет прав доступа. Пересоздайте вебхук с правами crm и user.")
except BitrixWebhookRateLimitError:
    logger.warning("Превышен лимит запросов. Повторите через 1 секунду.")
    time.sleep(1)
except BitrixWebhookConnectionError:
    logger.error("Нет подключения к интернету или Битрикс24 недоступен.")
```

### Коды ошибок HTTP

| Код | Исключение | Описание |
|-----|------------|----------|
| 404 | `BitrixWebhookNotFoundError` | Вебхук не найден |
| 403 | `BitrixWebhookForbiddenError` | Нет прав доступа |
| 429 | `BitrixWebhookRateLimitError` | Превышен лимит запросов |
| Timeout | `BitrixWebhookConnectionError` | Таймаут соединения |

---

## Rate Limiting

Битрикс24 ограничивает количество запросов:
- **2 запроса в секунду** для REST API
- **10000 запросов в день** для некоторых методов

### Автоматическая обработка

Клиент автоматически обрабатывает 429 ошибки с экспоненциальной задержкой:

```python
# Внутренняя реализация
def make_request(self, method: str, params: dict = None) -> dict:
    for attempt in range(3):
        response = requests.post(url, json={...}, timeout=30)
        
        if response.status_code == 429:
            delay = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(delay)
            continue
        
        response.raise_for_status()
        return response.json()
    
    raise BitrixWebhookRateLimitError("Превышен лимит запросов")
```

### Рекомендации

1. **Кэшируйте результаты** при частом чтении одних и тех же данных
2. **Используйте пакетные запросы** для получения больших объёмов данных
3. **Избегайте опросов** в цикле без задержек

---

## Примеры использования

### Полный цикл работы с лидами

```python
from modules.bitrix_webhook import BitrixWebhookClient
from modules.exceptions import BitrixWebhookError

# Инициализация
client = BitrixWebhookClient(webhook_url, config)

# Проверка подключения
if not client.test_connection():
    print("Ошибка подключения к Битрикс24")
    exit(1)

# Получение новых лидов
try:
    leads = client.get_new_leads()
    print(f"Найдено {len(leads)} новых лидов")
    
    # Получение списка менеджеров
    managers = client.get_managers()
    manager_ids = [m['ID'] for m in managers if m['ACTIVE']]
    
    # Распределение лидов по менеджерам (round-robin)
    for i, lead in enumerate(leads):
        manager_id = manager_ids[i % len(manager_ids)]
        
        # Назначение лида
        success = client.assign_lead(
            lead_id=lead['ID'],
            manager_id=manager_id
        )
        
        if success:
            print(f"Лид {lead['ID']} назначен на менеджера {manager_id}")
        
        # Обновление статуса
        client.update_lead_status(
            lead_id=lead['ID'],
            status="В работе"
        )
        
except BitrixWebhookError as e:
    print(f"Ошибка Битрикс24: {e}")
```

### Массовое создание лидов

```python
leads_data = [
    {
        "TITLE": "Лид 1",
        "PHONE": "79991111111",
        "EMAIL": "lead1@example.com"
    },
    {
        "TITLE": "Лид 2",
        "PHONE": "79992222222",
        "EMAIL": "lead2@example.com"
    },
]

created_ids = []

for lead_data in leads_data:
    try:
        lead_id = client.create_lead(lead_data)
        created_ids.append(lead_id)
        print(f"Создан лид {lead_id}")
    except BitrixWebhookError as e:
        print(f"Ошибка создания лида: {e}")

print(f"Всего создано: {len(created_ids)}")
```

### Экспорт лидов в CSV

```python
import csv

leads = client.get_new_leads()

with open('leads_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    
    # Заголовок
    writer.writerow(['ID', 'Название', 'Телефон', 'Email', 'Статус'])
    
    # Данные
    for lead in leads:
        writer.writerow([
            lead.get('ID', ''),
            lead.get('TITLE', ''),
            lead.get('PHONE', ''),
            lead.get('EMAIL', ''),
            lead.get('STATUS_ID', '')
        ])

print(f"Экспортировано {len(leads)} лидов")
```

---

## Тестирование

### Моки для тестов

```python
# tests/test_bitrix_webhook.py
import pytest
from unittest.mock import Mock, patch
from modules.bitrix_webhook import BitrixWebhookClient

@pytest.fixture
def mock_config():
    return {"bitrix": {"stage": "Новая заявка"}}

def test_get_new_leads(mock_config):
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
        mock_post.assert_called_once()

def test_create_lead(mock_config):
    client = BitrixWebhookClient("https://test.bitrix24.ru/rest/1/code/", mock_config)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"result": "123"}
        
        lead_id = client.create_lead({
            "TITLE": "Тестовый лид",
            "PHONE": "79991234567"
        })
        
        assert lead_id == "123"
```

---

## Ссылки

- [REST API Битрикс24 — Лиды](https://training.bitrix24.ru/rest_help/crm/leads/)
- [REST API Битрикс24 — Сделки](https://training.bitrix24.ru/rest_help/crm/deals/)
- [REST API Битрикс24 — Компании](https://training.bitrix24.ru/rest_help/crm/companies/)
- [REST API Битрикс24 — Контакты](https://training.bitrix24.ru/rest_help/crm/contacts/)
- [REST API Битрикс24 — Пользователи](https://training.bitrix24.ru/rest_help/users/)

---

**Версия документации:** 1.0  
**Дата обновления:** 20 марта 2026 г.
