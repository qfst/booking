from pydantic import BaseModel, Field

from app.core.constants import JWT_BEARER


class LoginResponse(BaseModel):
    """Схема ответа на аутентификацию."""

    access_token: str = Field(
        description='JWT токен для доступа к защищенным эндпоинтам',
    )
    token_type: str = Field(
        default=JWT_BEARER,
        description='Тип токена',
        examples=[JWT_BEARER],
    )
