from datetime import date
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.dialects.postgresql import insert

from app.core.context import get_current_session
from app.db.entities import Booking
from app.db.entities.booking import BookingRoomSlotProjection


class BookingRepository:
    """Репозиторий для выполнения операций с сущностями бронирования в базе данных."""

    @staticmethod
    async def get_bookings_with_rooms_and_slots_by_date(
        target_date: date,
    ) -> list[BookingRoomSlotProjection]:
        """Возвращает список всех комнат с временными слотами и статусом на дату.

        :param target_date: Целевая дата для проверки статусов бронирования.
        :return: Список проекций комнат со слотами времени.
        """
        query = text("""
                    SELECT
                        r.id AS room_id,
                        r.name AS room_name,
                        ts.id AS time_slot_id,
                        ts.start_time as time_slot_start_time,
                        ts.end_time as time_slot_end_time,
                        b.id as booking_id,
                        CASE
                            WHEN b.id IS NOT NULL THEN 'BOOKED'
                            ELSE 'FREE'
                        END AS status
                    FROM rooms r
                    CROSS JOIN time_slots ts
                    LEFT JOIN bookings b
                        ON b.room_id = r.id
                        AND b.slot_id = ts.id
                        AND b.date = :target_date
                    ORDER BY r.name, ts.start_time
                """)

        result = await get_current_session().execute(
            query,
            {'target_date': target_date},
        )

        rows = result.mappings().all()
        return [BookingRoomSlotProjection(**row) for row in rows]

    @staticmethod
    async def find_by_id(booking_id: UUID) -> Booking | None:
        """Ищет бронирование в базе данных по его идентификатору.

        :param booking_id: Идентификатор бронирования.
        :return: Сущность бронирования, если запись найдена.
        """
        result = await get_current_session().execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def is_exists_by(
        room_id: UUID,
        time_slot_id: UUID,
        booking_date: date,
    ) -> bool:
        """Проверяет существование бронирования на указанную комнату, дату и слот.

        :param room_id: Идентификатор комнаты.
        :param time_slot_id: Идентификатор слота времени.
        :param booking_date: Дата бронирования.
        :return: True, если бронирование уже существует.
        """
        return await get_current_session().scalar(
            select(
                select(Booking.id)
                .where(
                    Booking.room_id == room_id,
                    Booking.slot_id == time_slot_id,
                    Booking.date == booking_date,
                )
                .exists()
            )
        )

    @staticmethod
    async def create(booking: Booking) -> Booking:
        """Сохраняет новую запись бронирования в базе данных.

        :param booking: Сущность создаваемого бронирования.
        :return: Сохраненная сущность бронирования, возвращенная из базы данных.
        """
        return await get_current_session().scalar(
            insert(Booking)
            .values(
                id=booking.id,
                date=booking.date,
                room_id=booking.room_id,
                slot_id=booking.slot_id,
                user_id=booking.user_id,
            )
            .returning(Booking)
        )

    @staticmethod
    async def delete(booking_id: UUID) -> None:
        """Удаляет запись бронирования из базы данных по ее идентификатору.

        :param booking_id: Идентификатор бронирования.
        """
        await get_current_session().execute(
            delete(Booking).where(Booking.id == booking_id)
        )
