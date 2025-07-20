import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pathlib import Path
import httpx

from src.log import setup_logger
from src.config import config
from src.keycloak_api.client import KeycloakClient
from src.keycloak_api.router import keycloak_router
from src.keycloak_api.config import config_keycloak
from src.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Цикл жизни приложения FastAPI."""
    # Создаем и сохраняем shared httpx клиент
    http_client = httpx.AsyncClient()
    app.state.keycloak_client = KeycloakClient(http_client)

    yield

    # Закрываем httpx клиент при прекращении работы приложения
    await http_client.aclose()


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
    # Регистрируем обработчик исключений
    @app.exception_handler(HTTPException)
    async def auth_exception_handler(request: Request, exc: HTTPException):
        """В случае любой ошибки со статусом 401(Unauthorized) выкидывает в keycloak"""
        if exc.status_code == 401:
            return RedirectResponse(config_keycloak.keycloak_url)
        raise exc

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
