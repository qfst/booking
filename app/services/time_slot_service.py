import logging
from uuid import UUID

from app.core.decorators import with_session
from app.core.exceptions import TimeSlotNotFoundError
from app.db.entities import TimeSlot
from app.db.repositories.time_slot_repository import TimeSlotRepository


logger = logging.getLogger(__name__)


class TimeSlotService:
    """Сервис для управления временными слотами."""

    @with_session(transaction_read_only=True)
    async def get_time_slot(self, time_slot_id: UUID) -> TimeSlot:
        """Получает сущность временного слота.

        :param time_slot_id: Идентификатор слота времени.
        :return: Сущность найденного временного слота.
        :raises: TimeSlotNotFoundError: Если временный слот не найден.
        """
        logger.debug(
            f'Запрос на получение временного слота time_slot_id={time_slot_id}'
        )

        time_slot = await TimeSlotRepository.find_by_id(time_slot_id)
        if not time_slot:
            logger.warning(f'Временный слот с time_slot_id={time_slot_id} не найден')
            raise TimeSlotNotFoundError(time_slot_id)

        return time_slot
