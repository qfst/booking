import logging
from uuid import UUID

from app.core.decorators import with_session
from app.core.exceptions import CredentialsInvalidError, UserNotFoundError
from app.core.security import is_password_valid
from app.db.entities import User
from app.db.entities.user import UserRole
from app.db.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class UserService:
    """Сервис управления пользователями."""

    @with_session(transaction_read_only=True)
    async def authenticate(self, login: str, password: str) -> User:
        """Аутентифицирует и возвращает пользователя.

        :param login: Логин пользователя.
        :param password: Сырой пароль пользователя.
        :return: Сущность аутентифицированного пользователя.
        :raises CredentialsInvalidError: Если пользователь с таким логином не найден
            или введен неверный пароль.
        """
        logger.debug(f'Попытка аутентификации для login={login}')

        user: User = await UserRepository.find_by_login(login)
        if not user or not is_password_valid(password, user.password):
            logger.warning(
                f'Неудачная попытка входа: неверные учетные данные для login={login}'
            )
            raise CredentialsInvalidError()

        logger.info(
            f'Пользователь успешно аутентифицирован: user_id={user.id} role={user.role}'
        )
        return user

    @with_session(transaction_read_only=True)
    async def get_user(self, user_id: UUID) -> User:
        """Получает сущность пользователя.

        :param user_id: Идентификатор пользователя.
        :return: Сущность найденного пользователя.
        :raises UserNotFound: Если пользователь не найден.
        """
        user: User = await UserRepository.find_by_id(user_id)
        if not user:
            logger.warning(f'Пользователь с user_id={user_id} не найден')
            raise UserNotFoundError()
        return user

    @staticmethod
    def is_admin(user: User) -> bool:
        """Проверяет, обладает ли пользователь правами администратора.

        :param user: Сущность проверяемого пользователя.
        :return: True, если пользователь является администратором.
        """
        return user.role == UserRole.ADMIN
