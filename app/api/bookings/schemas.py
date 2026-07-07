from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.entities.booking import BookingStatus


class BookingCreateRequest(BaseModel):
    """Схема запроса на создание бронирования."""

    room_id: UUID = Field(description='Идентификатор комнаты')
    time_slot_id: UUID = Field(description='Идентификатор временного слота')
    booking_date: date = Field(description='Дата бронирования', examples=['2026-01-01'])


class BookingCreateResponse(BaseModel):
    """Схема ответа при создании бронирования."""

    id: UUID = Field(description='Идентификатор бронирования')
    room_id: UUID = Field(description='Идентификатор забронированной комнаты')
    time_slot_id: UUID = Field(
        description='Идентификатор забронированного временного слота',
    )
    booking_date: date = Field(
        description='Дата оформленного бронирования',
        examples=['2026-01-01'],
    )


class BookingSlotResponse(BaseModel):
    """Схема ответа для временного слота."""

    id: UUID = Field(description='Идентификатор временного слота')
    start_time: time = Field(description='Время начала слота', examples=['09:00:00'])
    end_time: time = Field(description='Время окончания слота', examples=['11:00:00'])
    booking_id: UUID | None = Field(
        default=None,
        description='Идентификатор бронирования',
    )
    status: BookingStatus = Field(description='Текущий статус доступности слота')


class BookingRoomSlotsResponse(BaseModel):
    """Схема ответа статуса бронированных комнат, включающая список временных слотов."""

    room_id: UUID = Field(description='Идентификатор комнаты')
    room_name: str = Field(description='Название переговорной комнаты')
    slots: list[BookingSlotResponse] = Field(
        default_factory=list,
        description='Список временных слотов, связанных с комнатой',
    )
