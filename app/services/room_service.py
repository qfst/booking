import logging
from uuid import UUID

from app.core.decorators import with_session
from app.core.exceptions import RoomNotFoundError
from app.db.repositories.room_repository import RoomRepository


logger = logging.getLogger(__name__)


class RoomService:
    """Сервис для работы с комнатами."""

    @with_session(transaction_read_only=True)
    async def validate_room_exists(self, room_id: UUID) -> None:
        """Проверяет существование комнаты.

        :param room_id: Идентификатор комнаты.
        :raises: RoomNotFoundError: Если комната не найдена.
        """
        if not await RoomRepository.is_exists_by(room_id):
            logger.warning(
                f'Проверка существования комнаты провалена: room_id={room_id}'
            )
            raise RoomNotFoundError(room_id)
        logger.debug(
            f'Валидация существования комнаты room_id={room_id} успешно пройдена'
        )
