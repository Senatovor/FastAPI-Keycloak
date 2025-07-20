from fastapi import Depends, Request, HTTPException, status
from loguru import logger

from .client import KeycloakClient
from .exceptions import NotAccessToken, InvalidToken
from .utils import get_payload
from .schemas import AddUser


def get_keycloak_client(request: Request) -> KeycloakClient:
    """Возвращает клиент Keycloak из состояния приложения.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        KeycloakClient: Клиент для работы с Keycloak.
    """
    return request.app.state.keycloak_client


async def get_token_from_cookie(request: Request) -> str | None:
    """Извлекает access token из cookie запроса.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        str | None: Access token или None, если токен отсутствует.
    """
    return request.cookies.get("access_token")


async def get_cookie_user(
    token: str = Depends(get_token_from_cookie),
) -> AddUser:
    """Получает информацию о пользователе из токена в cookie.

    Args:
        token (str): Access token, полученный из cookie.

    Returns:
        AddUser: Объект с информацией о пользователе.

    Raises:
        NotAccessToken(401): Если токен отсутствует.
        InvalidToken(401): Если токен недействителен.
    """
    if not token:
        raise NotAccessToken

    try:
        user_info = await get_payload(token)
        user_info["id"] = user_info.pop("sub")
        return AddUser(**user_info)
    except Exception as e:
        logger.error(f'Проблема токена: {e}')
        raise InvalidToken


async def get_server_user(
    token: str = Depends(get_token_from_cookie),
    keycloak_client: KeycloakClient = Depends(get_keycloak_client),
) -> dict:
    """Получает информацию о пользователе от сервера Keycloak.

    Args:
        token (str): Access token, полученный из cookie.
        keycloak_client (KeycloakClient): Клиент Keycloak.

    Returns:
        dict: Словарь с информацией о пользователе.

    Raises:
        NotAccessToken(401): Если токен отсутствует.
        InvalidToken(401): Если токен недействителен или запрос к Keycloak не удался.
    """
    if not token:
        raise NotAccessToken

    try:
        user_info = await keycloak_client.get_user_info(token=token)
        return user_info
    except Exception as e:
        logger.error(f'Проблема токена: {e}')
        raise InvalidToken

