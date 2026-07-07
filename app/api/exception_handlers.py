import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.api.shared.errors import Error, LocationType, ValidationError
from app.api.shared.headers import HEADER_AUTHENTICATE
from app.core.constants import JWT_BEARER
from app.core.exceptions import (
    CredentialsInvalidError,
    InternalServerError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.core.messages import Message
from app.mappers.error_mapper import ErrorMapper


logger = logging.getLogger(__name__)


def credentials_invalid_handler(
    request,
    exc: CredentialsInvalidError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='login',
                    detail=Message.CREDENTIALS_INVALID,
                    location_type=LocationType.BODY,
                ),
                ValidationError(
                    field='password',
                    detail=Message.CREDENTIALS_INVALID,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
    )


def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.critical(f'Необработанное системное исключение: {exc}', exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Error(message=Message.INTERNAL_ERROR).model_dump(mode='json'),
    )


def request_validation_handler(request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorMapper.map(exc).model_dump(mode='json'),
    )


def internal_server_handler(request, exc: InternalServerError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Error(message=str(exc)).model_dump(mode='json'),
    )


def token_expired_handler(request, exc: TokenExpiredError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='access_token',
                    detail=Message.TOKEN_EXPIRED,
                    location_type=LocationType.HEADER,
                ),
            ],
        ).model_dump(mode='json'),
        headers={HEADER_AUTHENTICATE: JWT_BEARER},
    )


def token_invalid_handler(request, exc: TokenInvalidError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='access_token',
                    detail=Message.TOKEN_INVALID,
                    location_type=LocationType.HEADER,
                ),
            ],
        ).model_dump(mode='json'),
        headers={HEADER_AUTHENTICATE: JWT_BEARER},
    )


HANDLERS_REGISTRY = [
    (CredentialsInvalidError, credentials_invalid_handler),
    (Exception, unhandled_exception_handler),
    (RequestValidationError, request_validation_handler),
    (InternalServerError, internal_server_handler),
    (TokenExpiredError, token_expired_handler),
    (TokenInvalidError, token_invalid_handler),
]


def register_all_exception_handlers(app: FastAPI) -> None:
    for exception_class, handler_function in HANDLERS_REGISTRY:
        app.add_exception_handler(exception_class, handler_function)
