import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pwdlib import PasswordHash

from app.api.shared.common import TokenPayload
from app.core.config import settings
from app.core.exceptions import (
    TokenExpiredError,
    TokenGenerationError,
    TokenInvalidError,
)


logger = logging.getLogger(__name__)

_pwd_hash = PasswordHash.recommended()

JWT_ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(user_id: UUID) -> str:
    """Генерирует токен доступа (JWT) для пользователя.

    :param user_id: Уникальный идентификатор пользователя.
    :return: Закодированный JWT-токен.
    :raises TokenGenerationError: Ошибка при генерации JWT.
    """
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = TokenPayload(
        sub=user_id,
        exp=int(expire.timestamp()),
        iat=int(now.timestamp()),
    )

    try:
        token = jwt.encode(
            claims=token_payload.model_dump(mode='json'),
            key=settings.SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        logger.info(f'Выпущен токен доступа для user_id={user_id}')
        return token
    except JWTError as e:
        logger.critical(f'Критический сбой JWT: {e}', exc_info=True)
        raise TokenGenerationError() from e


def is_password_valid(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие сырого пароля его хэшу.

    :param plain_password: Пароль в открытом виде, переданный пользователем.
    :param hashed_password: Хэш пароля из базы данных.
    :return: True, если пароль верный.
    """
    return _pwd_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием алгоритма argon2 и случайной salt.

    :param password: Сырой пароль для хэширования.
    :return: Хэш пароля.
    """
    hashed_password = _pwd_hash.hash(password)
    logger.debug('Выполнено хэширование пароля')
    return hashed_password


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    """Декодирует и валидирует JWT-токен.

    :param token: Токен, извлеченный из заголовка Authorization.
    :return: Объект с валидированными данными токена.
    :raises TokenExpiredError: Если срок действия токена истек.
    :raises TokenInvalidError: Если подпись неверна или токен поврежден.
    """
    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        validated_payload = TokenPayload.model_validate(payload)

        logger.debug(f'Успешная валидация токена для user_id={validated_payload.sub}')
        return validated_payload

    except ExpiredSignatureError as e:
        logger.warning('Отказ в доступе: срок действия токена истек')
        raise TokenExpiredError() from e

    except JWTError as e:
        logger.warning(f'Отказ в доступе: невалидный токен или подпись {e}')
        raise TokenInvalidError() from e
