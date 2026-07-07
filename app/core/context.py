import logging
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SessionMissingError


_session_context: ContextVar[AsyncSession | None] = ContextVar('session', default=None)

logger = logging.getLogger(__name__)


def is_session_active() -> bool:
    """Проверяет, привязана ли активная сессия к текущему контексту выполнения.

    :return: True, если сессия существует и активна.
    """
    return _session_context.get() is not None


def get_current_session() -> AsyncSession:
    """Возвращает текущую активную сессию базы данных из контекста.

    :return: Экземпляр активной асинхронной сессии SQLAlchemy.
    :raises SessionMissingError: Если метод вызван вне области действия декоратора
            @with_session
    """
    session = _session_context.get()
    if not session:
        logger.critical(
            'Попытка обращения к базе данных без открытой сессии. '
            'Возможно, метод сервиса или репозитория не обернут в @with_session'
        )
        raise SessionMissingError()
    return session


def set_current_session(session: AsyncSession) -> Token[AsyncSession | None]:
    """Устанавливает сессию базы данных в текущий контекст выполнения.

    :param session: Экземпляр открытой асинхронной сессии SQLAlchemy.
    :return: Токен контекста, необходимый для последующего сброса состояния.
    """
    logger.debug(f'Установка сессии {id(session)} в контекст выполнения')
    return _session_context.set(session)


def reset_current_session(token: Token[AsyncSession | None]) -> None:
    """Сбрасывает состояние контекста сессии к предыдущему значению по токену.

    :param token: Токен контекста, полученный при вызове set_current_session.
    """
    logger.debug('Сброс и очистка сессии из контекста выполнения')
    _session_context.reset(token)
