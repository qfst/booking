from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import time_machine
from httpx import AsyncClient
from starlette import status

from app.api.bookings.schemas import BookingCreateRequest, BookingCreateResponse
from app.api.shared.errors import Error, LocationType, ValidationError
from app.api.shared.headers import (
    HEADER_AUTHENTICATE,
    HEADER_AUTHORIZATION,
    HEADER_TIMEZONE,
)
from app.core.config import settings
from app.core.constants import JWT_BEARER
from app.core.messages import Message
from app.core.security import create_access_token
from app.db.entities.booking import BookingStatus
from app.db.entities.user import UserRole
from tests.integration.conftest import PATH_BOOKING
from tests.integration.db_utils import (
    create_booking,
    delete_booking,
    get_bookings_with_rooms_and_slots_first,
    get_time_slots,
    get_user_by_role,
    is_booking_room_slot_first_status_free,
)
from tests.integration.utils import (
    get_header_token,
    get_today,
    get_tomorrow_date,
    is_errors_equals,
)


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_created(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)
    assert room_with_slot.status == BookingStatus.FREE

    request = BookingCreateRequest(
        room_id=room_with_slot.room_id,
        time_slot_id=room_with_slot.time_slot_id,
        booking_date=tomorrow,
    )
    created_booking_id = None
    try:
        response = await client.post(PATH_BOOKING, json=request.model_dump(mode='json'))
        assert response.status_code == status.HTTP_201_CREATED
        room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)
        assert room_with_slot.status == BookingStatus.BOOKED

        actual = BookingCreateResponse.model_validate(response.json())
        created_booking_id = actual.id
        expected = BookingCreateResponse(
            id=created_booking_id,
            room_id=room_with_slot.room_id,
            time_slot_id=room_with_slot.time_slot_id,
            booking_date=tomorrow,
        )
        assert actual == expected
    finally:
        if created_booking_id:
            await delete_booking(created_booking_id)
        assert await is_booking_room_slot_first_status_free(tomorrow)


@pytest.mark.parametrize('client', ['anonymous'], indirect=True)
async def test_error_date_time_expired(client: AsyncClient):
    time_slots = await get_time_slots()
    today = get_today()
    target_time = datetime.combine(
        date=today,
        time=time_slots[1].start_time,
        tzinfo=settings.TIMEZONE_DEFAULT,
    )

    with time_machine.travel(target_time):
        room_with_slot = await get_bookings_with_rooms_and_slots_first(today)
        employee = await get_user_by_role(UserRole.EMPLOYEE)

        request = BookingCreateRequest(
            room_id=room_with_slot.room_id,
            time_slot_id=room_with_slot.time_slot_id,
            booking_date=today,
        )
        headers = {
            HEADER_AUTHORIZATION: get_header_token(create_access_token(employee.id)),
        }
        response = await client.post(
            PATH_BOOKING,
            json=request.model_dump(mode='json'),
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        time_slot_date_time = datetime.combine(
            date=today,
            time=time_slots[0].end_time,
            tzinfo=settings.TIMEZONE_DEFAULT,
        )
        actual = Error.model_validate(response.json())
        expected = Error(
            message=Message.BOOKING_DATE_TIME_EXPIRED(
                time_slot_date_time=time_slot_date_time, now_date_time=target_time
            ),
            errors=[
                ValidationError(
                    field='time_slot_id',
                    detail=Message.DATE_OR_TIME_EXPIRED,
                    location_type=LocationType.BODY,
                ),
            ],
        )
        assert actual == expected


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_room_not_found(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)

    request = BookingCreateRequest(
        room_id=uuid4(),
        time_slot_id=room_with_slot.time_slot_id,
        booking_date=tomorrow,
    )
    response = await client.post(
        PATH_BOOKING,
        json=request.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.ROOM_NOT_FOUND(room_id=request.room_id),
        errors=[
            ValidationError(
                field='room_id',
                detail=Message.NOT_FOUND,
                location_type=LocationType.BODY,
            ),
        ],
    )
    assert actual == expected


@pytest.mark.parametrize('client', ['anonymous'], indirect=True)
async def test_error_user_not_found_or_locked(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)

    request = BookingCreateRequest(
        room_id=room_with_slot.room_id,
        time_slot_id=room_with_slot.time_slot_id,
        booking_date=tomorrow,
    )
    headers = {HEADER_AUTHORIZATION: get_header_token(create_access_token(uuid4()))}
    response = await client.post(
        PATH_BOOKING,
        json=request.model_dump(mode='json'),
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.headers[HEADER_AUTHENTICATE] == JWT_BEARER

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.USER_NOT_FOUND,
        errors=[
            ValidationError(
                field=HEADER_AUTHORIZATION,
                detail=Message.TOKEN_INVALID,
                location_type=LocationType.HEADER,
            )
        ],
    )
    assert actual == expected


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_time_slot_not_found(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)

    request = BookingCreateRequest(
        room_id=room_with_slot.room_id,
        time_slot_id=uuid4(),
        booking_date=tomorrow,
    )
    response = await client.post(
        PATH_BOOKING,
        json=request.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.TIME_SLOT_NOT_FOUND(time_slot_id=request.time_slot_id),
        errors=[
            ValidationError(
                field='time_slot_id',
                detail=Message.NOT_FOUND,
                location_type=LocationType.BODY,
            )
        ],
    )
    assert actual == expected


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_already_exists(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)
    admin = await get_user_by_role(UserRole.ADMIN)
    booking = await create_booking(room_with_slot, tomorrow, admin.id)

    try:
        request = BookingCreateRequest(
            room_id=room_with_slot.room_id,
            time_slot_id=room_with_slot.time_slot_id,
            booking_date=tomorrow,
        )
        response = await client.post(
            PATH_BOOKING,
            json=request.model_dump(mode='json'),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

        actual = Error.model_validate(response.json())
        expected = Error(
            message=Message.BOOKING_ALREADY_EXISTS(
                room_id=request.room_id,
                time_slot_id=request.time_slot_id,
                booking_date=request.booking_date,
            ),
            errors=[
                ValidationError(
                    field='booking_date',
                    detail=Message.DATE_BOOKED,
                    location_type=LocationType.BODY,
                ),
                ValidationError(
                    field='room_id',
                    detail=Message.ROOM_BOOKED,
                    location_type=LocationType.BODY,
                ),
                ValidationError(
                    field='time_slot_id',
                    detail=Message.TIME_SLOT_BOOKED,
                    location_type=LocationType.BODY,
                ),
            ],
        )

        assert is_errors_equals(actual, expected)
    finally:
        await delete_booking(booking.id)
        assert await is_booking_room_slot_first_status_free(tomorrow)


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_date_expired(client: AsyncClient):
    today = get_today()
    yesterday = today - timedelta(days=1)
    room_with_slot = await get_bookings_with_rooms_and_slots_first(yesterday)

    request = {
        'room_id': str(room_with_slot.room_id),
        'time_slot_id': str(room_with_slot.time_slot_id),
        'booking_date': str(yesterday),
    }
    response = await client.post(PATH_BOOKING, json=request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.BOOKING_DATE_EXPIRED(yesterday, today),
        errors=[
            ValidationError(
                field='booking_date',
                detail=Message.DATE_OR_TIME_EXPIRED,
                location_type=LocationType.BODY,
            )
        ],
    )
    assert actual == expected


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_invalid_request(client: AsyncClient):
    headers = {HEADER_TIMEZONE: 'Invalid/Invalid'}
    request = {
        'room_id': 'invalid',
        'time_slot_id': 'invalid',
        'booking_date': 'invalid',
    }
    response = await client.post(PATH_BOOKING, json=request, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.VALIDATION_ERROR,
        errors=[
            ValidationError(
                field=HEADER_TIMEZONE,
                detail=Message.TIMEZONE_INVALID,
                location_type=LocationType.HEADER,
            ),
            ValidationError(
                field='room_id',
                detail=Message.UUID_INVALID,
                location_type=LocationType.BODY,
            ),
            ValidationError(
                field='time_slot_id',
                detail=Message.UUID_INVALID,
                location_type=LocationType.BODY,
            ),
            ValidationError(
                field='booking_date',
                detail=Message.DATE_INVALID,
                location_type=LocationType.BODY,
            ),
        ],
    )

    assert is_errors_equals(actual, expected)


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_empty_request(client: AsyncClient):
    response = await client.post(PATH_BOOKING, json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.VALIDATION_ERROR,
        errors=[
            ValidationError(
                field='room_id',
                detail=Message.MISSING_FIELD,
                location_type=LocationType.BODY,
            ),
            ValidationError(
                field='time_slot_id',
                detail=Message.MISSING_FIELD,
                location_type=LocationType.BODY,
            ),
            ValidationError(
                field='booking_date',
                detail=Message.MISSING_FIELD,
                location_type=LocationType.BODY,
            ),
        ],
    )

    assert is_errors_equals(actual, expected)
