from uuid import UUID

from sqlalchemy import select

from app.core.context import get_current_session
from app.db.entities import TimeSlot


class TimeSlotRepository:
    """Репозиторий для выполнения операций с сущностями слотов времени в базе данных."""

    @staticmethod
    async def find_by_id(time_slot_id: UUID) -> TimeSlot | None:
        """Ищет слот времени в базе данных по его идентификатору.

        :param time_slot_id: Идентификатор слота времени.
        :return: Сущность слота времени, если запись найдена.
        """
        result = await get_current_session().execute(
            select(TimeSlot).where(TimeSlot.id == time_slot_id)
        )
        return result.scalar_one_or_none()
