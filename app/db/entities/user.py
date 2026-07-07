import uuid
from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.config import Base


class UserRole(StrEnum):
    """Роли пользователей для разграничения прав доступа к системе."""

    ADMIN = 'admin'
    EMPLOYEE = 'employee'


class User(Base):
    """ORM-модель для представления учетной записи пользователя в базе данных.

    :param id: Уникальный идентификатор пользователя.
    :param login: Уникальный строковый логин для аутентификации.
    :param password: Захешированная строка пароля пользователя.
    :param role: Роль пользователя в системе, определяющая уровень его доступа.
    """

    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(10), nullable=False)
