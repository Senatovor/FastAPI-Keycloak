from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, HttpUrl
from pathlib import Path
from loguru import logger
from fastapi.templating import Jinja2Templates


class Config(BaseSettings):
    """Основной класс конфигурации приложения.

    Загружает настройки из .env файла или переменных окружения.

    Attributes:
        DB_HOST: Хост базы данных
        DB_PORT: Порт базы данных
        POSTGRES_DB: Имя базы данных
        POSTGRES_USER: Пользователь БД
        POSTGRES_PASSWORD: Пароль пользователя БД
        SECRET_KEY: Секретный ключ для JWT
        ALGORITHM: Алгоритм шифрования JWT
        ACCESS_TOKEN_EXPIRE: Время жизни access токена (в минутах)
        TITLE: Имя проекта
        VERSION: Версия проекта
        DESCRIPTION: Описание проекта (можно использовать синтаксис .md файлов):
        NAME_AUTHOR: Автор проекта
        URL_AUTHOR: Ссылка на автора проекта
        EMAIL_AUTHOR: Почта автора проекта
        DOCS_URL: http путь к документации docs
        REDOC_URL: http путь к документации redocs
        ROOT_PATH: http корневой путь проекта
        ROTATION: При каком условии происходит ротация логов
        LEVEL: Уровень логирования
        COMPRESSION: Формат сжатия логов
        BACKTRACE: Включает подробный трейсбек при ошибках
        DIAGNOSE: Добавляет информацию о переменных в стектрейс
        ENQUEUE: Асинхронная запись логов
        CATCH: Перехватывание исключения
    """
    # Настройки базы данных
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Настройки аутентификации
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int

    # Настройка приложения
    TITLE: str = 'FastAPI'
    VERSION: str = '1.0.0'
    DESCRIPTION: str | None = None
    NAME_AUTHOR: str | None = None
    URL_AUTHOR: HttpUrl | None = None
    EMAIL_AUTHOR: EmailStr | None = None
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None
    ROOT_PATH: str | None = None
    ROTATION: str | None = None
    LEVEL: str | None = None
    COMPRESSION: str | None = None
    BACKTRACE: bool
    DIAGNOSE: bool
    ENQUEUE: bool
    CATCH: bool

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding='utf-8'
    )

    @property
    def database_url(self) -> str:
        """Генерирует URL для подключения к PostgreSQL с использованием asyncpg."""
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}')

    @property
    def description_project(self) -> str:
        """Возвращает описание проекта"""
        return self.DESCRIPTION or None

    @property
    def contact_project(self) -> dict:
        """Возвращает контактные данные автора проекта"""
        return {
            "name": self.NAME_AUTHOR or None,
            "url": self.URL_AUTHOR or None,
            "email": self.EMAIL_AUTHOR or None,
        }


try:
    config = Config()
    templates = Jinja2Templates(
        directory=Path(__file__).parent.parent / "templates",
    )
except Exception as e:
    logger.error(f'Во время парсинга .env произошла ошибка: {e}')
