from datetime import date, datetime
from uuid import UUID


class Message:
    """Глобальный сборник сообщений об ошибках и уведомлений системы."""

    CREDENTIALS_INVALID = 'Неверный логин или пароль'
    DATE_BOOKED = 'Дата уже забронирована'
    DATE_INVALID = 'Неверный формат даты. Используйте YYYY-MM-DD'
    DATE_OR_TIME_EXPIRED = 'Дата или время истекли'
    INTERNAL_ERROR = 'Внутренняя ошибка сервера. Попробуйте позже'
    MISSING_FIELD = 'Это поле обязательно для заполнения'
    NOT_FOUND = 'Ресурс не найден'
    NO_PERMISSION = 'Нет прав'
    ROOM_BOOKED = 'Комната уже забронирована'
    STRING_INVALID = 'Значение должно быть строкой'
    TIMEZONE_INVALID = 'Указан некорректный или несуществующий часовой пояс'
    TIME_SLOT_BOOKED = 'Время уже забронировано'
    TOKEN_EXPIRED = 'Токен истек'
    TOKEN_INVALID = 'Токен невалиден'
    USER_NOT_FOUND = 'Пользователь не найден'
    UUID_INVALID = 'Значение должно быть валидным UUID'
    VALIDATION_ERROR = 'Ошибка валидации данных'

    @staticmethod
    def BOOKING_ALREADY_EXISTS(
        room_id: UUID,
        time_slot_id: UUID,
        booking_date: date,
    ) -> str:
        return (
            f'Комната {room_id} на дату {booking_date} '
            f'и слот времени {time_slot_id} уже забронирована'
        )

    @staticmethod
    def BOOKING_DATE_EXPIRED(booking_date: date, today: date) -> str:
        return (
            f'Нельзя оформить бронирование '
            f'на прошедшую дату: {booking_date.strftime("%d.%m.%Y")}, '
            f'текущая дата: {today.strftime("%d.%m.%Y")}'
        )

    @staticmethod
    def BOOKING_DATE_TIME_EXPIRED(
        time_slot_date_time: datetime,
        now_date_time: datetime,
    ) -> str:
        return (
            f'Временной слот истек {time_slot_date_time.strftime("%d.%m.%Y %H:%M")}, '
            f'текущее время: {now_date_time.strftime("%d.%m.%Y %H:%M")}'
        )

    @staticmethod
    def BOOKING_DELETE_NO_PERMISSION(booking_id: UUID) -> str:
        return f'Нельзя удалить бронь {booking_id}. Принадлежит другому пользователю'

    @staticmethod
    def BOOKING_NOT_FOUND(booking_id: UUID) -> str:
        return f'Бронь {booking_id} не найдена'

    @staticmethod
    def ROOM_NOT_FOUND(room_id: UUID) -> str:
        return f'Комната {room_id} не найдена'

    @staticmethod
    def TIME_SLOT_NOT_FOUND(time_slot_id: UUID) -> str:
        return f'Слот времени {time_slot_id} не найден'
