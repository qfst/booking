from uuid import UUID

from sqlalchemy import select

from app.core.context import get_current_session
from app.db.entities.user import User


class UserRepository:
    """Репозиторий для выполнения операций с сущностями пользователей в базе данных."""

    @staticmethod
    async def find_by_id(user_id: UUID) -> User | None:
        """Ищет пользователя в базе данных по его идентификатору.

        :param user_id: Идентификатор пользователя.
        :return: Сущность пользователя, если запись найдена.
        """
        result = await get_current_session().execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_by_login(login: str) -> User | None:
        """Ищет пользователя в базе данных по его логину.

        :param login: Логин пользователя.
        :return: Сущность пользователя, если запись найдена.
        """
        result = await get_current_session().execute(
            select(User).where(User.login == login)
        )
        return result.scalar_one_or_none()
