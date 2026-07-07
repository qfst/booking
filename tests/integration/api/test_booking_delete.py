from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status

from app.api.shared.errors import Error, LocationType, ValidationError
from app.core.messages import Message
from app.db.entities.user import UserRole
from tests.integration.conftest import PATH_BOOKING_DELETE
from tests.integration.db_utils import (
    create_booking,
    delete_booking,
    get_bookings_with_rooms_and_slots_first,
    get_user_by_role,
    is_booking_room_slot_first_status_free,
)
from tests.integration.utils import get_tomorrow_date


@pytest.mark.parametrize('client', ['admin', 'employee'], indirect=True)
async def test_deleted(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)
    employee = await get_user_by_role(UserRole.EMPLOYEE)
    booking = await create_booking(room_with_slot, tomorrow, employee.id)

    try:
        response = await client.delete(PATH_BOOKING_DELETE(booking.id))

        assert response.status_code == status.HTTP_204_NO_CONTENT
    except Exception:
        await delete_booking(booking.id)
    finally:
        assert await is_booking_room_slot_first_status_free(tomorrow)


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_not_found(client: AsyncClient):
    booking_id = uuid4()

    response = await client.delete(PATH_BOOKING_DELETE(booking_id))

    assert response.status_code == status.HTTP_404_NOT_FOUND

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.BOOKING_NOT_FOUND(booking_id),
        errors=[
            ValidationError(
                field='booking_id',
                detail=Message.NOT_FOUND,
                location_type=LocationType.PATH,
            ),
        ],
    )
    assert actual == expected


@pytest.mark.parametrize('client', ['employee'], indirect=True)
async def test_error_no_permission_booking(client: AsyncClient):
    tomorrow = get_tomorrow_date()
    room_with_slot = await get_bookings_with_rooms_and_slots_first(tomorrow)
    admin = await get_user_by_role(UserRole.ADMIN)
    booking = await create_booking(room_with_slot, tomorrow, admin.id)

    try:
        response = await client.delete(PATH_BOOKING_DELETE(booking.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

        actual = Error.model_validate(response.json())
        expected = Error(
            message=Message.BOOKING_DELETE_NO_PERMISSION(booking.id),
            errors=[
                ValidationError(
                    field='booking_id',
                    detail=Message.NO_PERMISSION,
                    location_type=LocationType.PATH,
                ),
            ],
        )
        assert actual == expected
    finally:
        await delete_booking(booking.id)
        assert await is_booking_room_slot_first_status_free(tomorrow)


@pytest.mark.parametrize('client', ['employee'], indirect=True)
@pytest.mark.parametrize(
    'booking_id', [True, 123, 'invalid'], ids=['boolean', 'int', 'str']
)
async def test_error_invalid_path(client: AsyncClient, booking_id: Any):
    response = await client.delete(PATH_BOOKING_DELETE(booking_id))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.VALIDATION_ERROR,
        errors=[
            ValidationError(
                field='booking_id',
                detail=Message.UUID_INVALID,
                location_type=LocationType.PATH,
            ),
        ],
    )
    assert actual == expected
