from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from fastapi import Depends
from typing import Annotated
from loguru import logger
from datetime import datetime

from src.config import config
from src.keycloak_api.config import config_keycloak

SQL_DATABASE_URL = config.database_url
SQL_DATABASE_KEYCLOAK_URL = config_keycloak.database_url

engine_app_db = create_async_engine(url=SQL_DATABASE_URL)
engine_keycloak_db = create_async_engine(url=SQL_DATABASE_KEYCLOAK_URL)

session_factory = async_sessionmaker(
    engine_app_db,
    expire_on_commit=False
)
session_factory_keycloak = async_sessionmaker(
    engine_keycloak_db,
    expire_on_commit=False
)


class DatabaseSessionManager:
    """
    Менеджер для управления асинхронными сессиями базы данных.

     Предоставляет:
    - Зависимости для FastAPI с настраиваемым уровнем изоляции
    - Декораторы для управления транзакциями
    - Автоматическое управление жизненным циклом сессии

    Args:
        session_maker: Фабрика сессий SQLAlchemy
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        """
        Инициализация менеджера сессий.

        Args:
            session_maker: Фабрика для создания асинхронных сессий
        """
        self.session_factory = session_maker

    def session_dependency(self, isolation_level: str | None = None, commit: bool = False):
        """
        Создает зависимость для FastAPI с настраиваемой сессией.

        1. Создает новую сессию с указанным уровнем изоляции (если задан)
        2. Предоставляет сессию в качестве зависимости
        3. Автоматически коммитит или откатывает изменения
        4. Гарантирует закрытие сессии

        Args:
            isolation_level: Уровень изоляции транзакции (например, "SERIALIZABLE")
            commit: Автоматически коммитить изменения после завершения

        Returns:
            Annotated[AsyncSession, Depends]: Зависимость для FastAPI
        """
        async def get_session():
            """Генератор сессии для зависимости FastAPI."""
            start_time = datetime.now()
            logger.info(f"Создание новой сессии. Изоляция: {isolation_level}, Автокоммит: {commit}")

            async with self.session_factory() as session:
                try:
                    if isolation_level:
                        logger.debug(f"Установка уровня изоляции: {isolation_level}")
                        await session.execute(
                            text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                        )
                    yield session
                    if commit:
                        logger.debug("Выполнение коммита изменений")
                        await session.commit()
                        logger.info("Изменения успешно закоммичены")
                except Exception as e:
                    logger.error(f"Ошибка в сессии: {str(e)}", exc_info=True)
                    await session.rollback()
                    logger.info("Выполнен откат транзакции")
                    raise
                finally:
                    await session.close()
                    exec_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Сессия закрыта. Время выполнения: {exec_time:.2f} сек")

        return Annotated[AsyncSession, Depends(get_session)]


# Глобальный экземпляр менеджера сессий
session_manager = DatabaseSessionManager(session_factory)
session_keycloak_manager = DatabaseSessionManager(session_factory_keycloak)

# Стандартная зависимость для FastAPI
SessionDepends = session_manager.session_dependency
SessionKeycloakDepends = session_keycloak_manager.session_dependency

# Пример использования зависимости для FastAPI
#
# @app.get("/")
# async def test(session: SessionDep(commit=True)):
#     session.add(User(name='Пеня', gender='MALE'))
#     return {"message": "User created"}
