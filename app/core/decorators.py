import logging
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import (
    is_session_active,
    reset_current_session,
    set_current_session,
)
from app.db.session_manager import create_session_manager


logger = logging.getLogger(__name__)

def with_session(transaction_read_only: bool):
    """Декоратор для автоматического управления сессией базы данных в функциях.

    Если сессия уже активна в текущем контексте выполнения, метод переиспользует ее,
    в противном случае создает новый экземпляр сессии через SessionManager.

    :param transaction_read_only: Флаг, указывающий на открытие транзакции в Read-Only
    :return: Обернутая функция с настроенным контекстом сессии базы данных.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if is_session_active():
                logger.debug(
                    f'Переиспользование существующей сессии базы данных для метода '
                    f'{func.__name__}'
                )
                return await func(*args, **kwargs)

            logger.debug(
                f'Открытие новой сессии базы данных для метода {func.__name__} '
                f'Read-Only: {transaction_read_only}'
            )

            async with await create_session_manager(
                transaction_read_only=transaction_read_only
            ) as session_manager:
                session: AsyncSession = await session_manager.session
                token = set_current_session(session)
                try:
                    return await func(*args, **kwargs)
                finally:
                    reset_current_session(token)

        return wrapper

    return decorator
