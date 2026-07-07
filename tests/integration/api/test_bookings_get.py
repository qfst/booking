from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from pydantic import TypeAdapter
from starlette import status

from app.api.bookings.schemas import BookingRoomSlotsResponse
from app.api.shared.errors import Error, LocationType, ValidationError
from app.core.messages import Message
from app.db.entities.booking import BookingStatus
from app.db.entities.user import UserRole
from tests.integration.conftest import PATH_BOOKING
from tests.integration.db_utils import (
    create_booking,
    get_bookings_with_rooms_and_slots_first,
    get_rooms,
    get_time_slots,
    get_user_by_role,
)
from tests.integration.utils import get_today


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_get_booking_rooms_with_slots(client: AsyncClient):
    today = get_today()
    room_slot = await get_bookings_with_rooms_and_slots_first(today)
    admin = await get_user_by_role(UserRole.ADMIN)
    booking = await create_booking(room_slot, today, admin.id)
    rooms = await get_rooms()
    time_slots = await get_time_slots()

    response = await client.get(PATH_BOOKING)

    assert response.status_code == status.HTTP_200_OK

    actual = TypeAdapter(list[BookingRoomSlotsResponse]).validate_python(
        response.json()
    )

    assert len(actual) == len(rooms)

    for actual_room, expected_room in zip(actual, rooms, strict=False):
        assert actual_room.room_id == expected_room.id
        assert actual_room.room_name == expected_room.name

        assert len(actual_room.slots) == len(time_slots)

        for actual_slot, expected_slot in zip(
            actual_room.slots,
            time_slots,
            strict=False,
        ):
            assert actual_slot.id == expected_slot.id
            assert actual_slot.start_time == expected_slot.start_time
            assert actual_slot.end_time == expected_slot.end_time
            if actual_slot.booking_id:
                assert actual_slot.booking_id == booking.id
                assert actual_slot.status == BookingStatus.BOOKED
            else:
                assert actual_slot.status == BookingStatus.FREE


@pytest.mark.parametrize('client', ['employee'], indirect=True)
@pytest.mark.parametrize(
    'target_date',
    [True, 123, 'invalid', uuid4()],
    ids=['boolean', 'int', 'str', 'uuid'],
)
async def test_error_invalid_query(client: AsyncClient, target_date: Any):
    query_params = {'target_date': target_date}
    response = await client.get(PATH_BOOKING, params=query_params)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.VALIDATION_ERROR,
        errors=[
            ValidationError(
                field='target_date',
                detail=Message.DATE_INVALID,
                location_type=LocationType.QUERY,
            ),
        ],
    )
    assert actual == expected
