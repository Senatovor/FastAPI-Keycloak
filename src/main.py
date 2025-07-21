import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pathlib import Path
import httpx
from sqladmin import Admin
from typing import Callable

from src.log import setup_logger
from src.config import config
from src.database.session import engine
from src.keycloak_api.client import KeycloakClient
from src.keycloak_api.router import keycloak_router
from src.keycloak_api.config import config_keycloak
from src.keycloak_api.dependencies import is_realm_admin_user, get_keycloak_client, get_token_from_cookie
from src.router import router
from src.admin.models import UserAdmin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Цикл жизни приложения FastAPI."""
    # Создаем и сохраняем shared httpx клиент
    http_client = httpx.AsyncClient()
    app.state.keycloak_client = KeycloakClient(http_client)

    yield

    # Закрываем httpx клиент при прекращении работы приложения
    await http_client.aclose()


def create_sql_admin_panel(app: FastAPI):
    """Создаем SQL админку и добавляем ей view-ы"""
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)


def create_app() -> FastAPI:
    """Фабрика для создания и настройки экземпляра FastAPI приложения.

    Returns:
        FastAPI: Настроенный экземпляр FastAPI приложения
    """
    # Создаем экземпляр приложения
    app = FastAPI(
        title=config.TITLE,
        version=config.VERSION,
        description=config.description_project,
        contact=config.contact_project,
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        root_path=config.ROOT_PATH,
        lifespan=lifespan,
    )

    # Добавляем middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


    # Регистрируем middleware admin
    @app.middleware("http")
    async def admin_permission_middleware(request: Request, call_next: Callable):
        # Пропускаем запросы не к /admin
        if not request.url.path.startswith("/admin"):
            return await call_next(request)

        try:
            token = await get_token_from_cookie(request)
            keycloak_client = get_keycloak_client(request)
            is_admin = await is_realm_admin_user(
                token=token,
                keycloak_client=keycloak_client
            )

            if not is_admin:
                logger.warning(f"Попытка войти в зону admin")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Доступ запрещен. Требуются права администратора"}
                )

            return await call_next(request)

        except Exception as e:
            logger.error(f"Ошибка проверки прав: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Доступ запрещен. Причина: {str(e)}"}
            )


    # Регистрируем обработчик исключений
    @app.exception_handler(HTTPException)
    async def auth_exception_handler(request: Request, exc: HTTPException):
        """В случае любой ошибки со статусом 401(Unauthorized) выкидывает в keycloak"""
        if exc.status_code == 401:
            return RedirectResponse(config_keycloak.keycloak_url)
        raise exc

    # Создаем sql админку
    create_sql_admin_panel(app)

    # Подключаем роуты и статические файлы
    app.include_router(keycloak_router)
    app.include_router(router)
    app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / 'static'), name="static")

    return app


if __name__ == '__main__':
    try:
        setup_logger()  # Настройки логирования
        logger.info('Создаю приложение FastAPI')
        app = create_app()

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            log_config=None,
            log_level=None,
        )
    except Exception as e:
        logger.error(f'Во время создания приложения произошла ошибка: {e}')
