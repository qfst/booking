import asyncio

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.api.shared.headers import HEADER_AUTHORIZATION
from app.core.config import BASE_DIR, settings
from app.core.security import create_access_token
from app.db.config import async_session_factory
from app.main import app
from tests.integration.db_utils import get_user_by_login
from tests.integration.utils import get_header_token


PATH_AUTH = '/auth/login'


@pytest.fixture(scope='session', autouse=True)
async def postgres_container():
    with PostgresContainer('postgres:18.4-alpine') as postgres:
        settings.POSTGRES_USER = postgres.username
        settings.POSTGRES_PASSWORD = postgres.password
        settings.POSTGRES_HOST = postgres.get_container_host_ip()
        settings.POSTGRES_PORT = postgres.get_exposed_port(5432)
        settings.POSTGRES_DB = postgres.dbname

        test_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,
            echo_pool='debug',
            poolclass=NullPool,
        )
        async_session_factory.configure(bind=test_engine)
        await _run_migrations()
        yield postgres
        await test_engine.dispose()


async def _run_migrations():
    alembic_cfg = Config(BASE_DIR / 'alembic.ini')
    await asyncio.to_thread(command.upgrade, alembic_cfg, 'head')


@pytest.fixture(scope='function', params=['anonymous', 'admin', 'employee'])
async def client(request) -> AsyncClient:
    headers = {}
    login = request.param

    if login != 'anonymous':
        user = await get_user_by_login(login)
        headers[HEADER_AUTHORIZATION] = get_header_token(create_access_token(user.id))

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
        headers=headers,
    ) as client:
        yield client
