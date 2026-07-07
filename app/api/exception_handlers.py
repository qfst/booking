import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.api.shared.errors import Error, LocationType, ValidationError
from app.api.shared.headers import HEADER_AUTHENTICATE, HEADER_AUTHORIZATION
from app.core.constants import JWT_BEARER
from app.core.exceptions import (
    BookingAlreadyExistsError,
    BookingDateExpiredError,
    BookingDateTimeExpiredError,
    BookingDeleteNoPermissionError,
    BookingNotFoundError,
    CredentialsInvalidError,
    InternalServerError,
    RoomNotFoundError,
    TimeSlotNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    UserNotFoundError,
)
from app.core.messages import Message
from app.mappers.error_mapper import ErrorMapper


logger = logging.getLogger(__name__)


def booking_already_exists_handler(
    request,
    exc: BookingAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='booking_date',
                    detail=Message.DATE_BOOKED,
                    location_type=LocationType.BODY,
                ),
                ValidationError(
                    field='room_id',
                    detail=Message.ROOM_BOOKED,
                    location_type=LocationType.BODY,
                ),
                ValidationError(
                    field='time_slot_id',
                    detail=Message.TIME_SLOT_BOOKED,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
    )


def booking_date_expired_handler(
    request,
    exc: BookingDateExpiredError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='booking_date',
                    detail=Message.DATE_OR_TIME_EXPIRED,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
    )


def booking_date_time_expired_handler(
    request,
    exc: BookingDateTimeExpiredError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='time_slot_id',
                    detail=Message.DATE_OR_TIME_EXPIRED,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
    )


def booking_delete_no_permission_handler(
    request,
    exc: BookingDeleteNoPermissionError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='booking_id',
                    detail=Message.NO_PERMISSION,
                    location_type=LocationType.PATH,
                ),
            ],
        ).model_dump(mode='json'),
    )


def booking_not_found_handler(
    request,
    exc: BookingNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='booking_id',
                    detail=Message.NOT_FOUND,
                    location_type=LocationType.PATH,
                ),
            ],
        ).model_dump(mode='json'),
    )


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


def room_not_found_handler(request, exc: RoomNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='room_id',
                    detail=Message.NOT_FOUND,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
    )


def internal_server_handler(request, exc: InternalServerError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Error(message=str(exc)).model_dump(mode='json'),
    )


def time_slot_not_found_handler(request, exc: TimeSlotNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field='time_slot_id',
                    detail=Message.NOT_FOUND,
                    location_type=LocationType.BODY,
                ),
            ],
        ).model_dump(mode='json'),
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


def user_not_found_handler(request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=Error(
            message=str(exc),
            errors=[
                ValidationError(
                    field=HEADER_AUTHORIZATION,
                    detail=Message.TOKEN_INVALID,
                    location_type=LocationType.HEADER,
                ),
            ],
        ).model_dump(mode='json'),
        headers={HEADER_AUTHENTICATE: JWT_BEARER},
    )


HANDLERS_REGISTRY = [
    (BookingAlreadyExistsError, booking_already_exists_handler),
    (BookingDateExpiredError, booking_date_expired_handler),
    (BookingDateTimeExpiredError, booking_date_time_expired_handler),
    (BookingDeleteNoPermissionError, booking_delete_no_permission_handler),
    (BookingNotFoundError, booking_not_found_handler),
    (CredentialsInvalidError, credentials_invalid_handler),
    (Exception, unhandled_exception_handler),
    (RequestValidationError, request_validation_handler),
    (RoomNotFoundError, room_not_found_handler),
    (InternalServerError, internal_server_handler),
    (TimeSlotNotFoundError, time_slot_not_found_handler),
    (TokenExpiredError, token_expired_handler),
    (TokenInvalidError, token_invalid_handler),
    (UserNotFoundError, user_not_found_handler),
]


def register_all_exception_handlers(app: FastAPI) -> None:
    for exception_class, handler_function in HANDLERS_REGISTRY:
        app.add_exception_handler(exception_class, handler_function)
