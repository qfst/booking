from uuid import UUID

from sqlalchemy import select

from app.core.context import get_current_session
from app.db.entities import Room


class RoomRepository:
    """Репозиторий для выполнения операций с сущностями комнат в базе данных."""

    @staticmethod
    async def is_exists_by(room_id: UUID) -> bool:
        """Проверяет существование комнаты в базе данных по ее идентификатору.

        :param room_id: Идентификатор комнаты.
        :return: True, если комната существует.
        """
        return await get_current_session().scalar(
            select(select(Room.id).where(Room.id == room_id).exists())
        )
