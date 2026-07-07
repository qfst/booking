import logging
from collections import OrderedDict
from uuid import UUID

from app.api.bookings.schemas import BookingRoomSlotsResponse, BookingSlotResponse
from app.db.entities.booking import BookingRoomSlotProjection


logger = logging.getLogger(__name__)


class BookingRoomSlotsMapper:
    """Преобразователь доменных проекций в объекты ответов API."""

    @staticmethod
    def map(
        projections: list[BookingRoomSlotProjection],
    ) -> list[BookingRoomSlotsResponse]:
        """Группирует плоский список проекций слотов по комнатам и преобразует в DTO.

        :param projections: Плоский список строк-проекций из базы данных.
        :return: Структированный список комнат со вложенными слотами.
        """
        logger.debug(
            f'Начало маппинга плоских проекций. Количество строк: {len(projections)}'
        )
        rooms: OrderedDict[UUID, BookingRoomSlotsResponse] = OrderedDict()

        for proj in projections:
            if proj.room_id not in rooms:
                rooms[proj.room_id] = BookingRoomSlotsResponse(
                    room_id=proj.room_id,
                    room_name=proj.room_name,
                )

            rooms[proj.room_id].slots.append(
                BookingSlotResponse(
                    id=proj.time_slot_id,
                    start_time=proj.time_slot_start_time,
                    end_time=proj.time_slot_end_time,
                    booking_id=proj.booking_id,
                    status=proj.status,
                )
            )

        logger.debug(f'Маппинг успешно завершен. Сгруппировано комнат: {len(rooms)}')
        return list(rooms.values())
