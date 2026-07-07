from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, Path, Query
from starlette import status

from app.api.bookings.schemas import (
    BookingCreateRequest,
    BookingCreateResponse,
    BookingRoomSlotsResponse,
)
from app.api.shared.common import TokenPayload
from app.api.shared.errors import Error
from app.api.shared.headers import Headers
from app.core.security import verify_token
from app.db.entities import Booking
from app.mappers.booking_room_slots_mapper import BookingRoomSlotsMapper
from app.services.booking_service import BookingService


router = APIRouter(prefix='/bookings', tags=['Bookings'])


@router.get(
    path='',
    description='Получает список бронирований комнат со статусами слотов.',
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Error},
    },
)
async def get_bookings(
    headers: Annotated[Headers, Header()],
    _: Annotated[TokenPayload, Depends(verify_token)],
    booking_service: Annotated[BookingService, Depends(BookingService)],
    target_date: Annotated[
        date | None,
        Query(
            description='Дата для получения списка бронирований комнат, '
            'если не указана, используется текущая дата',
        ),
    ] = None,
) -> list[BookingRoomSlotsResponse]:
    """Получает список бронирований на дату.

    :param headers: Заголовки запроса.
    :param _: Токен доступа пользователя (используется только для проверки авторизации)
    :param booking_service: Сервис для работы с бронированиями.
    :param target_date: Целевая дата для получения списка бронирований комнат.
    :return: Список комнат со сгруппированными внутри слотами.
    """
    if target_date is None:
        target_date = datetime.now(headers.x_timezone).date()
    return BookingRoomSlotsMapper.map(await booking_service.get_bookings(target_date))


@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    description='Создает бронирование.',
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Error},
    },
)
async def create_booking(
    request: Annotated[BookingCreateRequest, Body()],
    headers: Annotated[Headers, Header()],
    token_payload: Annotated[TokenPayload, Depends(verify_token)],
    booking_service: Annotated[BookingService, Depends(BookingService)],
) -> BookingCreateResponse:
    """Создает бронирование.

    :param request: Данные для создания бронирования.
    :param headers: Заголовки запроса.
    :param token_payload: Валидные данные JWT-токена текущего пользователя.
    :param booking_service: Сервис управления бронированиями.
    :return: Данные созданного бронирования.
    """
    booking: Booking = await booking_service.create_booking(
        request=request,
        user_id=token_payload.sub,
        timezone=headers.x_timezone,
    )

    return BookingCreateResponse(
        id=booking.id,
        room_id=booking.room_id,
        time_slot_id=booking.slot_id,
        booking_date=booking.date,
    )


@router.delete(
    path='/{booking_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Удаляет бронирование.',
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Error},
    },
)
async def delete_booking(
    booking_id: Annotated[UUID, Path()],
    token_payload: Annotated[TokenPayload, Depends(verify_token)],
    booking_service: Annotated[BookingService, Depends(BookingService)],
) -> None:
    """Удаляет бронирование.

    :param booking_id: Идентификатор бронирования.
    :param token_payload: Валидные данные JWT-токена текущего пользователя.
    :param booking_service: Сервис управления бронированиями.
    """
    await booking_service.delete_booking(
        booking_id=booking_id,
        user_id=token_payload.sub,
    )
