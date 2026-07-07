import uuid
from datetime import time

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.config import Base


class TimeSlot(Base):
    """ORM-модель для представления справочника слотов времени в базе данных.

    :param id: Уникальный идентификатор слота времени.
    :param start_time: Время начала слота времени.
    :param end_time: Время окончания слота времени.
    :param bookings: Связанная коллекция бронирований этого слота времени.
    """

    __tablename__ = 'time_slots'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    start_time: Mapped[time]
    end_time: Mapped[time]

    bookings = relationship(
        'Booking',
        back_populates='slot',
        cascade='all, delete-orphan',
    )
