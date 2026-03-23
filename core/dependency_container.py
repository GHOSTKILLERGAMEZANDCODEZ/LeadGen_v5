"""
Dependency Injection Container для приложения LeadGen v5.

Централизованное управление зависимостями для упрощения тестирования
и уменьшения связанности компонентов.
"""

import logging
from typing import Any

from database.db_manager import DatabaseManager
from database.models import init_database
from modules.services.processing_service import ProcessingService
from modules.bitrix_webhook import BitrixWebhookClient
from utils.config_loader import load_config

logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Контейнер зависимостей приложения.
    
    Предоставляет централизованное создание и управление сервисами.
    Реализует ленивую инициализацию (создание по требованию).
    
    Example:
        >>> container = DependencyContainer()
        >>> processing_service = container.get_processing_service()
        >>> bitrix_client = container.get_bitrix_client()
    """
    
    def __init__(self, config: dict | None = None):
        """
        Инициализирует контейнер зависимостей.
        
        Args:
            config: Конфигурация приложения. Если None, загружается из config.json.
        """
        self._config = config or load_config()
        self._db_manager: DatabaseManager | None = None
        self._processing_service: ProcessingService | None = None
        self._bitrix_client: BitrixWebhookClient | None = None
        
        logger.info("DependencyContainer инициализирован")
    
    @property
    def config(self) -> dict:
        """Возвращает конфигурацию приложения."""
        return self._config
    
    def get_db_manager(self) -> DatabaseManager:
        """
        Возвращает менеджер базы данных.
        
        Returns:
            DatabaseManager: Менеджер SQLite базы данных.
        """
        if self._db_manager is None:
            db_path = self._config["paths"]["database"]
            self._db_manager = DatabaseManager(db_path)
            init_database(db_path)
            logger.debug("DatabaseManager создан")
        return self._db_manager
    
    def get_processing_service(self) -> ProcessingService:
        """
        Возвращает сервис обработки данных.
        
        Returns:
            ProcessingService: Сервис для обработки файлов Webbee AI.
        """
        if self._processing_service is None:
            db_manager = self.get_db_manager()
            self._processing_service = ProcessingService(
                db_manager=db_manager,
                config=self._config
            )
            logger.debug("ProcessingService создан")
        return self._processing_service
    
    def get_bitrix_client(self) -> BitrixWebhookClient:
        """
        Возвращает клиент для работы с API Битрикс24.
        
        Returns:
            BitrixWebhookClient: Клиент для REST API Битрикс24.
        """
        if self._bitrix_client is None:
            webhook_url = self._config.get("bitrix_webhook", {}).get("webhook_url", "")
            if not webhook_url:
                logger.warning("BITRIX_WEBHOOK_URL не настроен")
            self._bitrix_client = BitrixWebhookClient(
                webhook_url=webhook_url,
                config=self._config
            )
            logger.debug("BitrixWebhookClient создан")
        return self._bitrix_client
