from datetime import date, time
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.config import Base


class Booking(Base):
    """ORM-модель для представления бронирования комнаты в базе данных.

    :param id: Уникальный идентификатор бронирования.
    :param date: Дата, на которую оформлено бронирование.
    :param room_id: Идентификатор забронированной комнаты.
    :param slot_id: Идентификатор временного слота.
    :param user_id: Идентификатор забронировавшего пользователя.
    :param room: Связанная сущность забронированной комнаты.
    :param slot: Связанная сущность выбранного временного слота.
    """

    __tablename__ = 'bookings'
    __table_args__ = (
        UniqueConstraint('date', 'slot_id', 'room_id', name='unique_booking'),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    date: Mapped[date]
    room_id: Mapped[UUID] = mapped_column(ForeignKey('rooms.id'))
    slot_id: Mapped[UUID] = mapped_column(ForeignKey('time_slots.id'))
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))

    room = relationship(
        'Room',
        back_populates='bookings',
        primaryjoin='Booking.room_id == Room.id',
        foreign_keys=[room_id],
        lazy='selectin',
    )

    slot = relationship(
        'TimeSlot',
        back_populates='bookings',
        primaryjoin='Booking.slot_id == TimeSlot.id',
        foreign_keys=[slot_id],
        lazy='selectin',
    )


class BookingStatus(StrEnum):
    """Статусы бронирования."""

    FREE = 'FREE'
    BOOKED = 'BOOKED'


class BookingRoomSlotProjection(BaseModel):
    """Объект проекции данных слота комнаты, возвращаемый репозиторием.

    Используется для оптимизированного вывода расписания на основе SQL-запроса,
    объединяющего комнаты, слоты и бронирования.

    :param room_id: Уникальный идентификатор комнаты.
    :param room_name: Уникальное название комнаты.
    :param time_slot_id: Уникальный идентификатор слота времени.
    :param time_slot_start_time: Время начала слота времени.
    :param time_slot_end_time: Время окончания слота времени.
    :param booking_id: Идентификатор бронирования (None, если слот свободен).
    :param status: Текущий статус доступности слота.
    """

    room_id: UUID
    room_name: str
    time_slot_id: UUID
    time_slot_start_time: time
    time_slot_end_time: time
    booking_id: UUID | None = None
    status: BookingStatus
