"""
Модуль логирования операций.

Настройка логгера для записи событий в файл и консоль.
"""

import logging
from pathlib import Path
from datetime import datetime

LEVEL_METHODS = {
    "debug": "debug",
    "warning": "warning",
    "error": "error",
    "info": "info",
}


def _ensure_log_dir(log_dir: str) -> Path:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def setup_logger(
    name: str = "leadgen", log_dir: str = "data/logs", level: int = logging.INFO
) -> logging.Logger:
    """
    Настраивает и возвращает логгер.

    Args:
        name: Имя логгера
        log_dir: Директория для логов
        level: Уровень логирования

    Returns:
        Настроенный логгер
    """
    # Создаём директорию для логов
    log_path = _ensure_log_dir(log_dir)

    # Формируем имя файла лога с датой
    log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Очищаем существующие обработчики
    logger.handlers.clear()
    logger.propagate = False

    # Формат сообщений
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Обработчик для записи в файл
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Глобальный логгер по умолчанию
default_logger: logging.Logger | None = None


def get_logger(name: str = "leadgen") -> logging.Logger:
    """
    Получает логгер (создаёт если не существует).

    Args:
        name: Имя логгера

    Returns:
        Логгер
    """
    global default_logger

    if default_logger is None:
        default_logger = setup_logger(name)

    return default_logger
