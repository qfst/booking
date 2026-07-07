from datetime import date, datetime
from uuid import UUID

from app.core.messages import Message


class BookingAlreadyExistsError(Exception):
    """Возникает если бронирование уже существует."""

    def __init__(self, room_id: UUID, time_slot_id: UUID, booking_date: date):
        super().__init__(
            Message.BOOKING_ALREADY_EXISTS(
                room_id=room_id,
                time_slot_id=time_slot_id,
                booking_date=booking_date,
            )
        )


class BookingDateExpiredError(Exception):
    """Возникает если дата бронирования меньше текущей даты."""

    def __init__(self, booking_date: date, today: date):
        super().__init__(
            Message.BOOKING_DATE_EXPIRED(booking_date=booking_date, today=today)
        )


class BookingDateTimeExpiredError(Exception):
    """Возникает при попытке забронировать прошедший слот времени.

    Момент окончания выбранного слота на указанную дату находится в прошлом
    относительно текущего времени.
    """

    def __init__(self, time_slot_date_time: datetime, now_date_time: datetime):
        super().__init__(
            Message.BOOKING_DATE_TIME_EXPIRED(
                time_slot_date_time=time_slot_date_time,
                now_date_time=now_date_time,
            )
        )


class BookingDeleteNoPermissionError(Exception):
    """Возникает если пользователь не является владельцем бронирования или админом."""

    def __init__(self, booking_id: UUID):
        super().__init__(Message.BOOKING_DELETE_NO_PERMISSION(booking_id))


class BookingNotFoundError(Exception):
    """Возникает если бронирование не найдено."""

    def __init__(self, booking_id: UUID):
        super().__init__(Message.BOOKING_NOT_FOUND(booking_id))


class CredentialsInvalidError(Exception):
    """Возникает если пользователя нет с таким логином или введен неверный пароль."""

    def __init__(self):
        super().__init__(Message.CREDENTIALS_INVALID)


class RoomNotFoundError(Exception):
    """Возникает если комната не найдена."""

    def __init__(self, room_id: UUID):
        super().__init__(Message.ROOM_NOT_FOUND(room_id))


class InternalServerError(Exception):
    """Базовое исключение для известных сбоев инфрастуктуры сервера."""

    def __init__(self):
        super().__init__(Message.INTERNAL_ERROR)


class SessionMissingError(InternalServerError):
    """Возникает при попытке выполнить запрос к базе данных вне контекста сессии."""


class TokenGenerationError(InternalServerError):
    """Возникает при ошибке криптографии во время создания JWT."""


class TimeSlotNotFoundError(Exception):
    """Возникает если слот времени не найден."""

    def __init__(self, time_slot_id: UUID):
        super().__init__(Message.TIME_SLOT_NOT_FOUND(time_slot_id))


class TokenExpiredError(Exception):
    """Возникает если токен истек по времени."""

    def __init__(self):
        super().__init__(Message.TOKEN_EXPIRED)


class TokenInvalidError(Exception):
    """Возникает если токен невалиден."""

    def __init__(self):
        super().__init__(Message.TOKEN_INVALID)


class UserNotFoundError(Exception):
    """Возникает если пользователь не найден."""

    def __init__(self):
        super().__init__(Message.USER_NOT_FOUND)
