from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from app.core.config import settings


HEADER_AUTHORIZATION = 'Authorization'
HEADER_AUTHENTICATE = 'WWW-Authenticate'
HEADER_TIMEZONE = 'X-Timezone'


class Headers(BaseModel):
    """Схема для валидации и парсинга заголовков запроса."""

    x_timezone: ZoneInfo = Field(
        default=settings.TIMEZONE_DEFAULT,
        description='Часовой пояс клиента для расчета локального времени бронирований',
        examples=[str(settings.TIMEZONE_DEFAULT)],
    )
