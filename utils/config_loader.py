"""
Модуль загрузки и сохранения конфигурации (config.json).

Поддерживает переменные окружения для чувствительных данных.
"""

import json
import os
import copy
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

DEFAULT_CONFIG = {
    "managers": ["Менеджер 1", "Менеджер 2", "Менеджер 3"],
    "processing": {
        "phone_format": "7",
        "remove_duplicates": True,
        "min_phone_length": 10,
        "ignore_phone_2": False,
    },
    "paths": {
        "input_dir": "data/input",
        "output_dir": "data/output",
        "database": "data/database.db",
    },
    "ui": {
        "theme": "dark",  # Только тёмная тема
        "font_family": "Segoe UI",
        "font_size": 10,
    },
    "bitrix": {
        "stage": "Новая заявка",
        "source": "Холодный звонок",
        "service_type": "ГЦК",
    },
    "bitrix_webhook": {
        "webhook_url": "",  # Загружается из переменных окружения
        "status_id": "Новая заявка",
        "max_leads_per_manager": 50,
        "excluded_managers": [],
    },
    "log_level": "INFO",
}

_CONFIG_CACHE: dict[str, Any] | None = None
_CONFIG_MTIME: float | None = None

_BOOL_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_BOOL_FALSE_VALUES = {"0", "false", "no", "n", "off"}


def _deepcopy_default() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_CONFIG)


def _merge_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
    merged = _deepcopy_default()
    _deep_merge(merged, config)
    return merged


def _get_config_mtime(config_path: Path) -> float | None:
    try:
        return config_path.stat().st_mtime
    except OSError:
        return None


def _update_cache(base_config: dict[str, Any], config_path: Path | None = None) -> None:
    global _CONFIG_CACHE, _CONFIG_MTIME
    _CONFIG_CACHE = base_config
    if config_path is None:
        config_path = get_config_path()
    _CONFIG_MTIME = _get_config_mtime(config_path)


def _get_cached_base_config() -> dict[str, Any]:
    config_path = get_config_path()
    mtime = _get_config_mtime(config_path)

    if _CONFIG_CACHE is not None and _CONFIG_MTIME == mtime:
        return _CONFIG_CACHE

    base_config = _load_base_config_from_disk(config_path)
    _update_cache(base_config, config_path)
    return base_config


def _load_base_config_from_disk(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        return _deepcopy_default()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return _merge_with_defaults(config)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return _deepcopy_default()


def _env_str(name: str, default: str = "") -> str:
    value = get_env_var(name, "")
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def _env_int(name: str, default: int) -> int:
    value = _env_str(name, "")
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = _env_str(name, "")
    if not value:
        return default
    value_lower = value.lower()
    if value_lower in _BOOL_TRUE_VALUES:
        return True
    if value_lower in _BOOL_FALSE_VALUES:
        return False
    return default


def _get_section(config: dict[str, Any], section: str, default: Any) -> Any:
    if section in config:
        return config[section]
    return copy.deepcopy(default)


def get_config_path() -> Path:
    """
    Возвращает путь к файлу конфигурации.

    Returns:
        Путь к config.json
    """
    return Path(__file__).parent.parent / "config.json"


def get_env_var(name: str, default: str = "") -> str:
    """
    Получает переменную окружения.

    Args:
        name: Имя переменной
        default: Значение по умолчанию

    Returns:
        Значение переменной окружения
    """
    return os.getenv(name, default)


def get_processing_settings() -> dict[str, Any]:
    """
    Получает настройки обработки данных из конфигурации.

    Returns:
        Словарь с настройками обработки:
        - phone_format: Формат телефона ('7', '8', '+7')
        - min_phone_length: Минимальная длина телефона
        - remove_duplicates: Удалять дубликаты
        - ignore_phone_2: Игнорировать Phone2 при проверке дубликатов
    """
    config = load_config()
    return config.get("processing", {})


def load_config() -> dict[str, Any]:
    """
    Загружает конфигурацию из config.json и переменных окружения.

    Returns:
        Словарь с конфигурацией
    """
    base_config = _get_cached_base_config()
    config = copy.deepcopy(base_config)
    _apply_env_variables(config)
    return config


def save_config(config: dict[str, Any]) -> bool:
    """
    Сохраняет конфигурацию в config.json.
    НЕ сохраняет чувствительные данные (вебхуки, токены).

    Args:
        config: Словарь с конфигурацией

    Returns:
        True, если сохранение успешно
    """
    config_path = get_config_path()

    try:
        # Создаём глубокую копию без чувствительных данных
        config_safe = copy.deepcopy(config)
        if "bitrix_webhook" in config_safe:
            # Не сохраняем webhook_url в файл
            config_safe["bitrix_webhook"]["webhook_url"] = ""

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_safe, f, indent=4, ensure_ascii=False)

        _update_cache(_merge_with_defaults(config_safe), config_path)
        return True
    except IOError as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False


def save_settings_section(section: str, settings: dict[str, Any]) -> bool:
    """
    Сохраняет секцию настроек в конфигурацию.

    Args:
        section: Название секции ('processing', 'ui', 'paths')
        settings: Словарь с настройками

    Returns:
        True, если сохранение успешно
    """
    config = load_config()

    # Глубокое объединение вместо полной замены
    if (
        section in config
        and isinstance(config[section], dict)
        and isinstance(settings, dict)
    ):
        config[section].update(settings)
    else:
        config[section] = settings

    return save_config(config)


def _apply_env_variables(config: dict[str, Any]) -> None:
    """
    Применяет переменные окружения к конфигурации.
    Тема UI НЕ загружается из переменных окружения, а берётся из config.json.

    Args:
        config: Словарь конфигурации (изменяется)
    """
    # Обработка
    processing = config.get("processing", {})
    processing["phone_format"] = _env_str(
        "PHONE_FORMAT", processing.get("phone_format", "7")
    )
    processing["min_phone_length"] = _env_int(
        "MIN_PHONE_LENGTH", int(processing.get("min_phone_length", 10))
    )
    processing["remove_duplicates"] = _env_bool(
        "REMOVE_DUPLICATES", bool(processing.get("remove_duplicates", True))
    )
    processing["ignore_phone_2"] = _env_bool(
        "IGNORE_PHONE_2", bool(processing.get("ignore_phone_2", False))
    )
    config["processing"] = processing

    # UI (тема НЕ загружается из переменных окружения!)
    ui = config.get("ui", {})
    ui["font_size"] = _env_int("UI_FONT_SIZE", int(ui.get("font_size", 10)))
    config["ui"] = ui

    # Пути
    paths = config.get("paths", {})
    paths["input_dir"] = _env_str("INPUT_DIR", paths.get("input_dir", "data/input"))
    paths["output_dir"] = _env_str(
        "OUTPUT_DIR", paths.get("output_dir", "data/output")
    )
    paths["database"] = _env_str(
        "DATABASE_PATH", paths.get("database", "data/database.db")
    )
    config["paths"] = paths

    # Вебхук
    webhook = config.get("bitrix_webhook", {})
    webhook["webhook_url"] = _env_str(
        "BITRIX_WEBHOOK_URL", webhook.get("webhook_url", "")
    )
    config["bitrix_webhook"] = webhook

    # Логирование
    config["log_level"] = _env_str("LOG_LEVEL", config.get("log_level", "INFO"))


def _deep_merge(base: dict, update: dict) -> None:
    """
    Глубокое объединение словарей (обновляет base значениями из update).

    Args:
        base: Базовый словарь (обновляется)
        update: Словарь с обновлениями
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
