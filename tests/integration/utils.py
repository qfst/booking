from datetime import date, datetime, timedelta

from app.api.shared.errors import Error
from app.core.config import settings
from app.core.constants import JWT_BEARER


def is_errors_equals(actual: Error, expected: Error) -> bool:
    return actual.message == expected.message and sorted(
        actual.errors, key=lambda x: x.field
    ) == sorted(expected.errors, key=lambda x: x.field)


def get_header_token(token: str) -> str:
    return f'{JWT_BEARER} {token}'


def get_now_datetime() -> datetime:
    return datetime.now(settings.TIMEZONE_DEFAULT)


def get_tomorrow_date() -> date:
    return get_today() + timedelta(days=1)


def get_today() -> date:
    return get_now_datetime().date()
