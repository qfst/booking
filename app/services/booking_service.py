import logging
from datetime import date, datetime
from typing import Annotated
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import Depends

from app.api.bookings.schemas import BookingCreateRequest
from app.core.decorators import with_session
from app.core.exceptions import (
    BookingAlreadyExistsError,
    BookingDateExpiredError,
    BookingDateTimeExpiredError,
    BookingDeleteNoPermissionError,
    BookingNotFoundError,
)
from app.db.entities import Booking
from app.db.entities.booking import BookingRoomSlotProjection
from app.db.repositories.booking_repository import BookingRepository
from app.services.room_service import RoomService
from app.services.time_slot_service import TimeSlotService
from app.services.user_service import UserService


logger = logging.getLogger(__name__)


class BookingService:
    """Сервис управления бронированиями.

    :param user_service: Сервис для работы с пользователями.
    :param room_service: Сервис для работы с комнатами.
    :param time_slot_service: Сервис для работы со слотами времени.
    """

    def __init__(
        self,
        user_service: Annotated[UserService, Depends(UserService)],
        room_service: Annotated[RoomService, Depends(RoomService)],
        time_slot_service: Annotated[TimeSlotService, Depends(TimeSlotService)],
    ):
        self._user_service: UserService = user_service
        self._room_service: RoomService = room_service
        self._time_slot_service: TimeSlotService = time_slot_service

    @with_session(transaction_read_only=True)
    async def get_bookings(self, target_date: date) -> list[BookingRoomSlotProjection]:
        """Получает список бронирований комнат со статусами их слотов на указанную дату.

        :param target_date: Дата, на которую запрашивается расписание бронирований.
        :return: Список проекций бронирований комнат со слотами и их статусом.
        """
        logger.debug(
            f'Запрос списка бронирований комнат со слотами на дату: {target_date}'
        )
        bookings = await BookingRepository.get_bookings_with_rooms_and_slots_by_date(
            target_date,
        )
        logger.debug(f'Успешно получено {len(bookings)} записей на дату: {target_date}')
        return bookings

    @with_session(transaction_read_only=False)
    async def delete_booking(self, booking_id: UUID, user_id: UUID) -> None:
        """Удаляет бронирование, если у пользователя есть на это права.

        :param booking_id: Идентификатор бронирования.
        :param user_id: Идентификатор пользователя.
        :raises BookingDeleteNoPermissionError: Если пользователь не является
                владельцем бронирования или администратором.
        """
        logger.debug(
            f'Начало процесса удаления бронирования booking_id={booking_id} '
            f'пользователем user_id={user_id}'
        )

        booking = await self.get_booking(booking_id)
        user = await self._user_service.get_user(user_id)

        if booking.user_id != user.id and not self._user_service.is_admin(user):
            logger.warning(
                f'Отказ в удалении бронирования booking_id={booking_id}. '
                f'Пользователь user_id={user.id} не имеет прав'
            )
            raise BookingDeleteNoPermissionError(booking.id)

        await BookingRepository.delete(booking.id)
        logger.info(
            f'Успешно удалено бронирование booking_id={booking_id} '
            f'пользователем user_id={user.id}'
        )

    @with_session(transaction_read_only=True)
    async def get_booking(self, booking_id: UUID) -> Booking:
        """Получает бронирование.

        :param booking_id: Идентификатор бронирования.
        :return: Сущность найденного бронирования.
        :raises BookingNotFoundError: Если бронирование не найдено.
        """
        booking = await BookingRepository.find_by_id(booking_id)
        if not booking:
            logger.warning(f'Бронирование с booking_id={booking_id} не найдено')
            raise BookingNotFoundError(booking_id)
        return booking

    @with_session(transaction_read_only=False)
    async def create_booking(
        self, request: BookingCreateRequest, user_id: UUID, timezone: ZoneInfo
    ) -> Booking:
        """Создание бронирования после прохождения всех валидаций.

        :param request: Данные для создания бронирования.
        :param user_id: Идентификатор пользователя.
        :param timezone: Часовой пояс.
        :return: Сущность созданного бронирования.
        """
        logger.debug(
            f'Старт валидации и создания бронирования для user_id={user_id}, '
            f'timezone={timezone}, request={request}'
        )
        now = datetime.now(timezone)

        self._validate_date(request.booking_date, now)

        await self._user_service.get_user(user_id=user_id)

        await self._validate_booking_not_exists(
            room_id=request.room_id,
            time_slot_id=request.time_slot_id,
            booking_date=request.booking_date,
        )

        await self._validate_date_time(
            booking_date=request.booking_date,
            time_slot_id=request.time_slot_id,
            now=now,
            timezone=timezone,
        )

        await self._room_service.validate_room_exists(room_id=request.room_id)

        created_booking = await BookingRepository.create(
            Booking(
                id=uuid4(),
                date=request.booking_date,
                room_id=request.room_id,
                slot_id=request.time_slot_id,
                user_id=user_id,
            ),
        )
        logger.info(
            f'Успешно создано бронирование booking_id={created_booking.id} '
            f'для user_id={user_id}, timezone={timezone}, request={request}'
        )
        return created_booking

    @staticmethod
    def _validate_date(booking_date: date, now: datetime) -> None:
        """Проверяет, что дата бронирования не находится в прошлом.

        :param booking_date: Проверяемая дата бронирования.
        :param now: Текущая дата и время.
        :raises BookingDateExpiredError: Если дата бронирования меньше текущей даты.
        """
        today = now.date()
        if booking_date < today:
            logger.warning(
                f'Валидация даты провалена: запрашиваемая дата '
                f'{booking_date} меньше текущей {today}'
            )
            raise BookingDateExpiredError(booking_date=booking_date, today=today)

    @with_session(transaction_read_only=True)
    async def _validate_booking_not_exists(
        self,
        room_id: UUID,
        time_slot_id: UUID,
        booking_date: date,
    ) -> None:
        """Проверяет отсутствие пересечений с уже существующими бронированиями.

        :param room_id: Идентификатор комнаты.
        :param time_slot_id: Идентификатор слота времени.
        :param booking_date: Дата бронирования.
        :raises BookingAlreadyExistsError: Если бронирование уже существует.
        """
        if await BookingRepository.is_exists_by(room_id, time_slot_id, booking_date):
            logger.warning(
                f'Валидация занятости провалена: комната room_id={room_id} '
                f'на слот time_slot_id={time_slot_id} и дату '
                f'booking_date={booking_date} уже занята'
            )
            raise BookingAlreadyExistsError(room_id, time_slot_id, booking_date)

    async def _validate_date_time(
        self,
        booking_date: date,
        time_slot_id: UUID,
        now: datetime,
        timezone: ZoneInfo,
    ) -> None:
        """Проверяет, что время окончания бронирования еще не наступило.

        :param booking_date: Дата бронирования.
        :param time_slot_id: Идентификатор слота времени.
        :param now: Текущая дата и время.
        :param timezone: Часовой пояс.
        :raises BookingDateTimeExpiredError: Если момент окончания слота на указанную
                дату находится в прошлом относительно текущего времени.
        """
        time_slot = await self._time_slot_service.get_time_slot(
            time_slot_id=time_slot_id,
        )
        slot_date_end_time = datetime.combine(
            date=booking_date,
            time=time_slot.end_time,
            tzinfo=timezone,
        )

        if slot_date_end_time < now:
            logger.warning(
                f'Валидация времени провалена: время окончания слота '
                f'{slot_date_end_time} уже прошло относительно текущего времени {now}'
            )
            raise BookingDateTimeExpiredError(
                time_slot_date_time=slot_date_end_time,
                now_date_time=now,
            )
