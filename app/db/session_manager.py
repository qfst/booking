import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.config import async_session_factory


logger = logging.getLogger(__name__)


class SessionManager:
    """Менеджер асинхронных сессий SQLAlchemy.

    Контекстный менеджер для управления жизненным циклом сессии.
    Автоматически контролирует открытие сессии, установку режима транзакции (Read-Only),
    фиксирует (commit) изменения при успехе или откатывает (rollback) при
    возникновении ошибок.
    """

    def __init__(self, transaction_read_only: bool):
        """Инициализирует менеджер сессий.

        :param transaction_read_only: Флаг, указывающий, что транзакция предназначена
                только для чтения данных.
        """
        self._session: AsyncSession = async_session_factory()
        self._transaction_read_only = transaction_read_only

    async def __aenter__(self):
        """Открывает асинхронный контекст и настраивает режим транзакции.

        :return: Текущей экземпляр менеджера сессий.
        """
        logger.debug(
            f'Инициализация новой сессии. Read-Only: {self._transaction_read_only}'
        )
        if self._transaction_read_only:
            await self._session.execute(text('SET TRANSACTION READ ONLY'))
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any
    ) -> None:
        """Закрывает асинхронный контекст, завершая или откатывая транзакцию.

        Очищает объект сессии после закрытия.

        :param exc_type: Тип возникшего исключения (если есть).
        :param exc_val: Экземпляр возникшего исключения (если есть).
        :param exc_tb: Трейсбэк возникшего исключения (если есть).
        """
        try:
            if self._transaction_read_only:
                logger.debug('Сессия Read-Only закрывается без фиксации изменений')
                return

            if exc_type:
                logger.error(
                    msg=f'Транзакция откатывается из-за необработанного исключения: '
                        f'{exc_type.__name__}: {exc_val}',
                    exc_info=True,
                )
                await self._session.rollback()
                logger.debug('Транзакция успешно откатилась')
            else:
                logger.debug('Транзакция начинает фиксацию')
                await self._session.commit()
                logger.debug('Транзакция успешно зафиксировалось')
        finally:
            await self._session.close()
            logger.debug('Асинхронная сессия базы данных успешно закрыта')
            self._session = None

    @property
    async def session(self) -> AsyncSession:
        """Возвращает текущую активную сессию базы данных.

        :return: Экземпляр активной сессии SQLAlchemy.
        """
        return self._session


async def create_session_manager(transaction_read_only: bool) -> SessionManager:
    """Функция для создания экземпляра SessionManager.

    :param transaction_read_only: Флаг режима Read-Only.
    :return: Новый настроенный экземпляр менеджера сессий.
    """
    return SessionManager(transaction_read_only)
