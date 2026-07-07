class Message:
    """Глобальный сборник сообщений об ошибках и уведомлений системы."""

    CREDENTIALS_INVALID = 'Неверный логин или пароль'
    DATE_INVALID = 'Неверный формат даты. Используйте YYYY-MM-DD'
    INTERNAL_ERROR = 'Внутренняя ошибка сервера. Попробуйте позже'
    MISSING_FIELD = 'Это поле обязательно для заполнения'
    STRING_INVALID = 'Значение должно быть строкой'
    TOKEN_EXPIRED = 'Токен истек'
    TOKEN_INVALID = 'Токен невалиден'
    VALIDATION_ERROR = 'Ошибка валидации данных'
