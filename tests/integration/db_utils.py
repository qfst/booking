from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select

from app.core.context import get_current_session
from app.core.decorators import with_session
from app.db.entities import Booking, TimeSlot, User
from app.db.entities.booking import BookingRoomSlotProjection, BookingStatus
from app.db.entities.room import Room
from app.db.entities.user import UserRole
from app.db.repositories.booking_repository import BookingRepository
from app.db.repositories.user_repository import UserRepository


@with_session(transaction_read_only=True)
async def get_user_by_role(role: UserRole) -> User:
    result = await get_current_session().execute(select(User).where(User.role == role))
    return result.scalar_one_or_none()


@with_session(transaction_read_only=True)
async def get_user_by_login(login: str) -> User:
    return await UserRepository.find_by_login(login)


@with_session(transaction_read_only=True)
async def is_booking_room_slot_first_status_free(booking_date: date):
    slot = await get_bookings_with_rooms_and_slots_first(booking_date)
    return slot.status == BookingStatus.FREE


@with_session(transaction_read_only=True)
async def get_bookings_with_rooms_and_slots_first(
    booking_date: date,
) -> BookingRoomSlotProjection:
    bookings = await get_bookings_with_rooms_and_slots(booking_date)
    return bookings[0]


@with_session(transaction_read_only=True)
async def get_bookings_with_rooms_and_slots(
    booking_date: date,
) -> list[BookingRoomSlotProjection]:
    return await BookingRepository.get_bookings_with_rooms_and_slots_by_date(
        booking_date,
    )


@with_session(transaction_read_only=False)
async def create_booking(
    proj: BookingRoomSlotProjection,
    booking_date: date,
    user_id: UUID,
) -> Booking:
    return await BookingRepository.create(
        Booking(
            id=uuid4(),
            date=booking_date,
            room_id=proj.room_id,
            slot_id=proj.time_slot_id,
            user_id=user_id,
        )
    )


@with_session(transaction_read_only=False)
async def delete_booking(booking_id: UUID) -> None:
    await BookingRepository.delete(booking_id)


@with_session(transaction_read_only=True)
async def get_rooms() -> list[Room]:
    result = await get_current_session().execute(select(Room).order_by(Room.name))
    return list(result.scalars().all())


@with_session(transaction_read_only=True)
async def get_time_slots() -> list[TimeSlot]:
    result = await get_current_session().execute(
        select(TimeSlot).order_by(TimeSlot.start_time)
    )
    return list(result.scalars().all())
