"""
Иерархия исключений для проекта LeadGen v5.

Модуль предоставляет специализированные исключения для различных сценариев:
- Ошибки Битрикс24 (вебхук, API)
- Ошибки обработки данных
- Ошибки валидации
- Ошибки экспорта
- Ошибки безопасности

Example:
    >>> from modules.exceptions import BitrixWebhookNotFoundError
    >>> try:
    ...     client.make_request("crm.lead.list")
    ... except BitrixWebhookNotFoundError as e:
    ...     logger.error(f"Вебхук не найден: {e}")
"""


class LeadGenError(Exception):
    """
    Базовое исключение для проекта LeadGen.
    
    Все специализированные исключения наследуются от этого класса.
    Это позволяет ловить все исключения проекта одним except LeadGenError.
    
    Attributes:
        message: Сообщение об ошибке
        original_exception: Оригинальное исключение (если есть)
    """
    
    def __init__(self, message: str, original_exception: Exception | None = None) -> None:
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке
            original_exception: Оригинальное исключение для цепочки
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
    
    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.message} (Причина: {self.original_exception})"
        return self.message


class SecurityError(LeadGenError):
    """
    Исключение безопасности (Path Traversal и т.п.).
    
    Выбрасывается при обнаружении попыток:
    - Выхода за пределы разрешённой директории
    - Доступа к системным файлам
    - Inject-атак через пользовательский ввод
    
    Example:
        >>> from modules.exceptions import SecurityError
        >>> if not is_safe_path(user_path):
        ...     raise SecurityError(f"Попытка Path Traversal: {user_path}")
    """
    pass


class BitrixWebhookError(LeadGenError):
    """
    Базовое исключение для ошибок Битрикс24.
    
    Все исключения, связанные с вебхуками Битрикс24, наследуются от этого класса.
    Позволяет ловить все ошибки Битрикс24 одним except BitrixWebhookError.
    """
    pass


class BitrixWebhookNotFoundError(BitrixWebhookError):
    """
    Вебхук не найден (404).
    
    Выбрасывается когда:
    - URL вебхука неверный
    - Вебхук удалён в Битрикс24
    - Недоступен портал Битрикс24
    
    Example:
        >>> try:
        ...     client.test_connection()
        ... except BitrixWebhookNotFoundError:
        ...     show_error("Вебхук не найден. Проверьте URL.")
    """
    pass


class BitrixWebhookForbiddenError(BitrixWebhookError):
    """
    Недостаточно прав (403).
    
    Выбрасывается когда:
    - У вебхука нет необходимых прав (crm, user)
    - Вебхук заблокирован администратором
    - Истёк срок действия вебхука
    
    Example:
        >>> try:
        ...     client.get_managers()
        ... except BitrixWebhookForbiddenError:
        ...     show_error("Нет прав. Пересоздайте вебхук с правами crm и user.")
    """
    pass


class BitrixWebhookRateLimitError(BitrixWebhookError):
    """
    Превышен лимит запросов (429).
    
    Выбрасывается когда:
    - API Битрикс24 вернуло 429 Too Many Requests
    - Превышен лимит запросов в секунду
    
    Example:
        >>> try:
        ...     client.get_new_leads_by_manager()
        ... except BitrixWebhookRateLimitError:
        ...     logger.warning("Rate limit. Ждём 1 секунду.")
        ...     time.sleep(1)
    """
    pass


class BitrixWebhookInvalidURLError(BitrixWebhookError):
    """
    Неверный формат URL вебхука.
    
    Выбрасывается когда:
    - URL не соответствует формату Битрикс24
    - URL пустой или None
    - URL не содержит обязательных компонентов
    
    Example:
        >>> try:
        ...     client = BitrixWebhookClient(invalid_url)
        ... except BitrixWebhookInvalidURLError:
        ...     show_error("Неверный формат вебхука")
    """
    pass


class BitrixWebhookConnectionError(BitrixWebhookError):
    """
    Ошибка подключения к Битрикс24.
    
    Выбрасывается когда:
    - Нет сетевого подключения
    - Таймаут соединения
    - SSL/TLS ошибка
    - DNS не разрешает домен
    
    Example:
        >>> try:
        ...     client.test_connection()
        ... except BitrixWebhookConnectionError:
        ...     show_error("Нет подключения к интернету или Битрикс24 недоступен")
    """
    pass


class ProcessingError(LeadGenError):
    """
    Ошибка обработки данных.
    
    Выбрасывается когда:
    - Ошибка при загрузке файла (неверный формат)
    - Ошибка при очистке данных
    - Ошибка при объединении файлов
    
    Example:
        >>> try:
        ...     df = process_file(filepath)
        ... except ProcessingError as e:
        ...     logger.error(f"Ошибка обработки: {e}")
    """
    pass


class ValidationError(LeadGenError):
    """
    Ошибка валидации данных.
    
    Выбрасывается когда:
    - Данные не проходят валидацию
    - Обязательные поля отсутствуют
    - Некорректный формат данных
    
    Example:
        >>> if not validate_phone(phone):
        ...     raise ValidationError(f"Неверный формат телефона: {phone}")
    """
    pass


class ExportError(LeadGenError):
    """
    Ошибка экспорта данных.
    
    Выбрасывается когда:
    - Ошибка записи файла
    - Недоступна директория для записи
    - Ошибка кодировки при экспорте
    
    Example:
        >>> try:
        ...     export_to_bitrix_csv(df, output_path)
        ... except ExportError as e:
        ...     logger.error(f"Ошибка экспорта: {e}")
    """
    pass
