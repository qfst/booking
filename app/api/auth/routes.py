from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.auth.schemas import LoginResponse
from app.api.shared.errors import Error
from app.core.security import create_access_token
from app.services.user_service import UserService


router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post(
    path='/login',
    description='Аутентификация пользователя и выдача токена доступа.',
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Error},
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(UserService)],
) -> LoginResponse:
    """Аутентификация пользователя и выдача токена доступа.

    :param form_data: Данные для аутентификации и создании токена.
    :param user_service: Сервис управления пользователями.
    :return: Токен доступа.
    """
    user = await user_service.authenticate(form_data.username, form_data.password)
    token = create_access_token(user.id)
    return LoginResponse(access_token=token)
