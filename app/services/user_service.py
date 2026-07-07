import logging

from app.core.decorators import with_session
from app.core.exceptions import CredentialsInvalidError
from app.core.security import is_password_valid
from app.db.entities import User
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
