from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.config import Base


class Room(Base):
    """ORM-модель для представления комнаты в базе данных.

    :param id: Уникальный идентификатор комнаты.
    :param name: Уникальное название комнаты.
    :param bookings: Связанная коллекция бронирований этой комнаты.
    """

    __tablename__ = 'rooms'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    bookings = relationship(
        'Booking',
        back_populates='room',
        cascade='all, delete-orphan',
        lazy='selectin',
        primaryjoin='Room.id == Booking.room_id',
    )
