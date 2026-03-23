"""
Конфигурация pytest для проекта.

Мокает matplotlib для тестов которые не используют pandas напрямую.
pandas и numpy должны быть реальными для тестов data_processor.
"""

import sys
import os

# Добавляем корень проекта в PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Не мокаем ничего - все зависимости должны быть реальными
# matplotlib мокаем только в тех тестах где он не используется
