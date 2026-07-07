from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse

from app.api.auth.routes import router as auth_router
from app.api.exception_handlers import (
    register_all_exception_handlers,
)
from app.db.config import verify_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Выполняет задачи на старте и выключении приложения."""
    await verify_db_connection()
    yield


app = FastAPI(title='Booking', lifespan=lifespan)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    """Автоматический редирект на страницу документации Swagger."""
    return RedirectResponse(url='/docs', status_code=status.HTTP_308_PERMANENT_REDIRECT)


app.include_router(auth_router)

register_all_exception_handlers(app)
