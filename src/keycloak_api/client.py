import httpx
from loguru import logger

from .config import config_keycloak
from .exceptions import TokenRequestError, InvalidToken, KeycloakRequestError


class KeycloakClient:
    """Класс для взаимодействия с Keycloak API.

    Предоставляет методы для обмена authorization code на токены и
    получения информации о пользователе.

    Attributes:
        client (httpx.AsyncClient): Асинхронный HTTP-клиент для запросов.

    Methods:
        get_tokens: Обменивает authorization code на токены.
        get_user_info: Получает информацию о пользователе по access_token.
    """
    def __init__(self, client: httpx.AsyncClient | None = None):
        """Инициализирует KeycloakClient.

        Args:
            client (httpx.AsyncClient | None): Опциональный HTTP-клиент.
            Если не передан, создается новый экземпляр.
        """
        self.client = client or httpx.AsyncClient()

    async def get_tokens(self, code: str) -> dict:
        """Обменивает authorization code на токены.

        Args:
            code (str): Authorization code, полученный от Keycloak.

        Returns:
            dict: Словарь с токенами (access_token, refresh_token и др.).

        Raises:
            TokenRequestError(401): Если запрос к Keycloak не удался или произошла ошибка.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            'redirect_uri': config_keycloak.redirect_uri,
            "client_id": config_keycloak.CLIENT_ID,
            "client_secret": config_keycloak.CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = await self.client.post(
                config_keycloak.token_url,
                data=data,
                headers=headers,
            )
            if response.status_code != 200:
                logger.error(f"Запрос токена не удался: {response.text}")
                raise TokenRequestError
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Обмен токенов не удался: {str(e)}")
            raise TokenRequestError

    async def get_user_info(self, token: str) -> dict:
        """Получает информацию о пользователе по access_token.

        Args:
            token (str): Access token, полученный от Keycloak.

        Returns:
            dict: Словарь с информацией о пользователе.

        Raises:
            InvalidToken(401): Если токен недействителен.
            KeycloakRequestError(500): Если токен произошла ошибка запроса.
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await self.client.get(
                config_keycloak.userinfo_url,
                headers=headers
            )
            if response.status_code != 200:
                logger.error(f'Не валидный access token: {response.text}')
                raise InvalidToken
            return response.json()
        except httpx.RequestError as e:
            logger.error(f'Ошибка при запросе к keycloak: {str(e)}')
            raise KeycloakRequestError

    async def check_user_admin_role(self, token: str, user_id: int) -> bool:
        """Проверяет, есть ли у пользователя роль администратора.

        Args:
            token (str): Access token пользователя.
            user_id (int): id пользователя

        Returns:
            bool: True, если у пользователя есть роль администратора, иначе False.

        Raises:
            InvalidToken: Если токен недействителен.
            KeycloakRequestError: Если произошла ошибка запроса.
        """
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = await self.client.get(
                config_keycloak.get_user_roles_url(user_id),
                headers=headers
            )

            admin_roles = ['realm-admin']

            if response.status_code != 200:
                logger.error(f"Ошибка при получении ролей: {response.text}")
                return False

            roles = response.json()
            client_roles = []
            for client_data in roles.get('clientMappings', {}).values():
                client_roles.extend(role['name'] for role in client_data.get('mappings', []))

            return any(role in admin_roles for role in client_roles)

        except httpx.RequestError as e:
            logger.error(f'Ошибка при запросе к Keycloak: {str(e)}')
            raise KeycloakRequestError
