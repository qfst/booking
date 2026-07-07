from sqlalchemy import select

from app.core.context import get_current_session
from app.core.decorators import with_session
from app.db.entities import User
from app.db.entities.user import UserRole
from app.db.repositories.user_repository import UserRepository


@with_session(transaction_read_only=True)
async def get_user_by_role(role: UserRole) -> User:
    result = await get_current_session().execute(select(User).where(User.role == role))
    return result.scalar_one_or_none()


@with_session(transaction_read_only=True)
async def get_user_by_login(login: str) -> User:
    return await UserRepository.find_by_login(login)
