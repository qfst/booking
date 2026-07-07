from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import time_machine

from app.core.config import settings
from app.core.exceptions import TokenExpiredError
from app.core.security import (
    create_access_token,
    hash_password,
    is_password_valid,
    verify_token,
)


def test_hash_password_uses_random_salt():
    password = 'password'

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two

    assert is_password_valid(password, hash_one)
    assert is_password_valid(password, hash_two)


def test_verify_token_expired():
    user_id = uuid4()

    iat = datetime.fromisoformat('2026-01-01 12:00:00Z')
    with time_machine.travel(iat):
        token = create_access_token(user_id)

    after_expire = iat + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    with time_machine.travel(after_expire), pytest.raises(TokenExpiredError):
        verify_token(token)
