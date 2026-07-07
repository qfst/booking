import logging

from sqlalchemy import AsyncAdaptedQueuePool, text
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.core.config import settings


logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)


@retry(
    retry=retry_if_exception_type((OSError, InterfaceError)),
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    reraise=True,
)
async def verify_db_connection() -> None:
    """Проверяет подключение к базе данных с повторными попытками."""
    logger.info('Проверка подключения к базе данных')
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        logger.info('Подключение к базе данных успешно установлено')
    except Exception as e:
        logger.error(f'Не удалось подключиться к базе данных: {e}', exc_info=True)
        raise e


class Base(DeclarativeBase):
    """Базовый класс декларативного маппинга для всех ORM-моделей.

    Используется Alembic и SQLAlchemy для автоматического обнаружения таблиц.
    """
