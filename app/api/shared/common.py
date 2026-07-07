from uuid import UUID

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Структура полезной нагрузки внутри JWT-токена."""

    sub: UUID = Field(description='ID пользователя (Subject)')
    exp: int = Field(description='Время истечения токена (Unix Timestamp)')
    iat: int = Field(description='Время выпуска токена (Unix Timestamp)')
