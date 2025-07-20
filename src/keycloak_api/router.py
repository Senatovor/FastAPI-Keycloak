from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from loguru import logger

from ..database.session import SessionDepends
from ..utils import error_response_docs
from .client import KeycloakClient
from .exceptions import NotCodeError, NotAccessToken, NotFoundUserIdError, AuthError
from .dependencies import get_keycloak_client
from .services import UserService
from .schemas import AddUser
from .config import config_keycloak
from .utils import get_payload

keycloak_router = APIRouter(prefix="/keycloak", tags=["keycloak"])


@keycloak_router.get(
    "/login/callback",
    name="keycloak_login_callback",
    response_class=RedirectResponse,
    summary="Обработка callback'а авторизации",
    description=
    """
    Обрабатывает callback от Keycloak после успешной аутентификации, 
    получает токены и создает пользователя если он не существует.
    """,
    responses={
        **error_response_docs(
            AuthError,
            'Ошибка авторизации'
        )
    }
)
async def login_callback(
        session: SessionDepends(commit=True),
        code: str | None = None,
        error: str | None = None,
        error_description: str | None = None,
        keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> RedirectResponse:
    """Обрабатывает callback от Keycloak после аутентификации.

    Args:
        session: Сессия базы данных.
        code: Код авторизации от Keycloak.
        error: Ошибка от Keycloak (если есть).
        error_description: Описание ошибки (если есть).
        keycloak: Клиент Keycloak.

    Returns:
        RedirectResponse: Перенаправление на защищенную страницу с установленными cookies.

    Raises:
        NotCodeError(401): Нету кода авторизации
        NotAccessToken(401): Нету access token
        NotFoundUserIdError(401): Не нашелся ID пользователя
        AuthError(401): Ошибка обработки callback'а
    """
    if error:
        logger.error(f'Ошибка keycloak: {error}, описание: {error_description}')
        raise NotCodeError

    if not code:
        logger.error(f'Нету кода авторизации')
        raise NotCodeError

    try:
        token_data = await keycloak.get_tokens(code)
        access_token = token_data.get('access_token')

        if not access_token:
            logger.error(f'Нету access token')
            raise NotAccessToken

        user_info = await get_payload(access_token)
        user_id = user_info.get('sub')
        if not user_id:
            logger.error(f'Не нашелся ID пользователя {user_id}')
            raise NotFoundUserIdError

        user = await UserService.find_by_id(session, user_id)
        if not user and isinstance(user_info, dict):
            user_info["id"] = user_info.pop("sub")
            logger.info('Создал юзера')
            await UserService.add(session, AddUser(**user_info))

        response = RedirectResponse(url="/protected")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        logger.info(f"Юзер {user_id} вошел успешно в систему")
        return response

    except Exception as e:
        logger.error(f"Ошибка обработки callback'а логина: {str(e)}")
        raise AuthError


@keycloak_router.get(
    '/logout',
    name="keycloak_logout",
    response_class=RedirectResponse,
    summary="Выход из системы",
    description=
    """
    Обрабатывает выход пользователя из системы,
    удаляет cookies и перенаправляет на страницу выхода Keycloak.
    """,
)
async def logout(request: Request):
    """Обрабатывает выход пользователя из системы.

    Args:
        request: Объект запроса FastAPI.

    Returns:
        RedirectResponse: Перенаправление на страницу выхода Keycloak
        с удаленными cookies аутентификации.
    """
    id_token = request.cookies.get('id_token')
    params = {
        "client_id": config_keycloak.CLIENT_ID,
        "post_logout_redirect_uri": config_keycloak.BASE_URL,
    }
    if id_token:
        params["id_token_hint"] = id_token

    keycloak_logout_url = f"{config_keycloak.logout_url}?{urlencode(params)}"
    response = RedirectResponse(url=keycloak_logout_url)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response
