from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from loguru import logger


class ConfigKeycloak(BaseSettings):
    """Класс конфигурации для Keycloak и базы данных.

    Загружает настройки из файла .env.keycloak или переменных окружения.
    Предоставляет свойства для формирования URL-адресов.

    Attributes:
        DB_HOST: Хост базы данных.
        DB_PORT: Порт базы данных.
        POSTGRES_DB: Имя базы данных.
        POSTGRES_USER: Пользователь базы данных.
        POSTGRES_PASSWORD: Пароль пользователя базы данных.
        CLIENT_SECRET: Секретный код клиента Keycloak.
        BASE_URL: Базовый URL приложения.
        KEYCLOAK_BASE_URL: Базовый URL Keycloak (внутренний).
        REALM: Название realm в Keycloak.
        CLIENT_ID: Идентификатор клиента в Keycloak.
        KEYCLOAK_EXTERNAL_URL: Внешний URL Keycloak.
        PUBLIC_KEY: Публичный ключ Keycloak.

        database_url: Формирует URL для подключения к PostgreSQL.
        token_url: URL для получения токенов.
        auth_url: URL для аутентификации.
        auth_url_extend: Внешний URL для аутентификации.
        logout_url: URL для выхода из системы.
        userinfo_url: URL для получения информации о пользователе.
        redirect_uri: URL для перенаправления после аутентификации.
        keycloak_url: Полный URL для аутентификации в Keycloak.
        get_user_roles_url: Возвращает URL для получения ролей пользователя в Keycloak.
    """
    # Настройки базы данных
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Настройки keycloak
    CLIENT_SECRET: str
    BASE_URL: str
    KEYCLOAK_BASE_URL: str
    REALM: str
    CLIENT_ID: str
    KEYCLOAK_EXTERNAL_URL: str
    PUBLIC_KEY: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env.keycloak",
        env_file_encoding='utf-8',
        extra='allow'
    )

    @property
    def database_url(self) -> str:
        """Формирует URL для подключения к PostgreSQL с использованием asyncpg."""
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}')

    @property
    def token_url(self) -> str:
        """Формирует URL для получения токенов в Keycloak."""
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/token"

    @property
    def auth_url(self) -> str:
        """Формирует URL для аутентификации в Keycloak."""
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/auth"

    @property
    def auth_url_extend(self) -> str:
        """Формирует внешний URL для аутентификации в Keycloak."""
        return f"{self.KEYCLOAK_EXTERNAL_URL}/realms/{self.REALM}/protocol/openid-connect/auth"

    @property
    def logout_url(self) -> str:
        """Формирует URL для выхода из системы в Keycloak."""
        return f"{self.KEYCLOAK_EXTERNAL_URL}/realms/{self.REALM}/protocol/openid-connect/logout"

    @property
    def userinfo_url(self) -> str:
        """Формирует URL для получения информации о пользователе."""
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/userinfo"

    @property
    def redirect_uri(self) -> str:
        """Формирует URL для перенаправления после аутентификации. (Куда будет кидать запрос keycloak)"""
        return f"{self.BASE_URL}/keycloak/login/callback"

    @property
    def keycloak_url(self) -> str:
        """Формирует полный URL для аутентификации в Keycloak."""
        return (
            f"{self.auth_url_extend}"
            f"?client_id={self.CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid"
            f"&redirect_uri={self.redirect_uri}"
        )

    def get_user_roles_url(self, user_id: int) -> str:
        """Возвращает URL для получения ролей пользователя в Keycloak.

        Args:
            user_id (str): ID пользователя в Keycloak (не username!).

        Returns:
            str: Полный URL для запроса ролей пользователя.
        """
        return f"{self.KEYCLOAK_BASE_URL}/admin/realms/{self.REALM}/users/{user_id}/role-mappings"


try:
    config_keycloak = ConfigKeycloak()
except Exception as e:
    logger.error(f'Во время парсинга .env.keycloak произошла ошибка: {e}')
