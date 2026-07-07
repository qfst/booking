import pytest
from httpx import AsyncClient
from starlette import status

from app.api.auth.schemas import LoginResponse
from app.api.shared.errors import Error, LocationType, ValidationError
from app.core.constants import JWT_BEARER
from app.core.messages import Message
from app.core.security import verify_token
from tests.integration.conftest import PATH_AUTH
from tests.integration.db_utils import get_user_by_login
from tests.integration.utils import is_errors_equals


@pytest.mark.parametrize('client', ['anonymous'], indirect=True)
@pytest.mark.parametrize(
    'login, password',
    [
        ('admin', 'admin'),
        ('employee', 'employee'),
    ],
    ids=['admin', 'employee'],
)
async def test_login(
    client: AsyncClient,
    login: str,
    password: str,
):
    request = {'username': login, 'password': password}
    response = await client.post(PATH_AUTH, data=request)

    assert response.status_code == status.HTTP_200_OK

    response_body = LoginResponse.model_validate(response.json())
    token_payload = verify_token(response_body.access_token)
    user = await get_user_by_login(request['username'])

    assert response_body.token_type == JWT_BEARER
    assert response_body.access_token is not None

    assert token_payload.exp > token_payload.iat
    assert token_payload.sub == user.id


@pytest.mark.parametrize('client', ['anonymous'], indirect=True)
@pytest.mark.parametrize(
    'login, password',
    [
        ('admin', 'invalid'),
        ('invalid', 'admin'),
    ],
    ids=['invalid_password', 'invalid_login'],
)
async def test_login_error_invalid_credentials(
    client: AsyncClient,
    login: str,
    password: str,
):
    request = {'username': login, 'password': password}
    response = await client.post(PATH_AUTH, data=request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.CREDENTIALS_INVALID,
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
    )
    assert is_errors_equals(actual, expected)


@pytest.mark.parametrize('client', ['anonymous'], indirect=True)
async def test_login_error_empty_request(client: AsyncClient):
    response = await client.post(PATH_AUTH, data={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    actual = Error.model_validate(response.json())
    expected = Error(
        message=Message.VALIDATION_ERROR,
        errors=[
            ValidationError(
                field='username',
                detail=Message.MISSING_FIELD,
                location_type=LocationType.BODY,
            ),
            ValidationError(
                field='password',
                detail=Message.MISSING_FIELD,
                location_type=LocationType.BODY,
            ),
        ],
    )
    assert is_errors_equals(actual, expected)
