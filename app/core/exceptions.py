from app.core.messages import Message


class CredentialsInvalidError(Exception):
    """Возникает если пользователя нет с таким логином или введен неверный пароль."""

    def __init__(self):
        super().__init__(Message.CREDENTIALS_INVALID)


class InternalServerError(Exception):
    """Базовое исключение для известных сбоев инфрастуктуры сервера."""

    def __init__(self):
        super().__init__(Message.INTERNAL_ERROR)


class SessionMissingError(InternalServerError):
    """Возникает при попытке выполнить запрос к базе данных вне контекста сессии."""


class TokenGenerationError(InternalServerError):
    """Возникает при ошибке криптографии во время создания JWT."""


class TokenExpiredError(Exception):
    """Возникает если токен истек по времени."""

    def __init__(self):
        super().__init__(Message.TOKEN_EXPIRED)


class TokenInvalidError(Exception):
    """Возникает если токен невалиден."""

    def __init__(self):
        super().__init__(Message.TOKEN_INVALID)
