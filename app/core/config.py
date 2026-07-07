from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Конфигурация окружения и настроек приложения, загружаемая из файла .env.

    :param SECRET_KEY: Секретный ключ для подписи JWT-токенов.
    :param ACCESS_TOKEN_EXPIRE_MINUTES: Время жизни токена доступа в минутах
    :param POSTGRES_USER: Имя пользователя для подключения к PostgreSQL
    :param POSTGRES_PASSWORD: Пароль для подключения к PostgreSQL
    :param POSTGRES_HOST: Адрес сервера базы данных PostgreSQL
    :param POSTGRES_PORT: Порт для подключения к PostgreSQL
    :param POSTGRES_DB: Имя целевой базы данных PostgreSQL
    """
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        """Формирует асинхронную строку подключения к PostgreSQL.

        :return: Полный URL подключения с драйвером asyncpg
        """
        return (
            f'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}@'
            f'{self.POSTGRES_HOST}:'
            f'{self.POSTGRES_PORT}/'
            f'{self.POSTGRES_DB}'
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
    )


settings = Settings()
