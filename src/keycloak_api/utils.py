from jose import jwt

from .config import config_keycloak


def get_public_key() -> str:
    """Формирует публичный ключ Keycloak в PEM-формате.

    Возвращает:
        str: Публичный ключ в формате PEM с заголовками.
    """
    return (
        f"-----BEGIN PUBLIC KEY-----\n"
        f"{config_keycloak.PUBLIC_KEY}"
        f"\n-----END PUBLIC KEY-----"
    )


async def get_payload(token) -> dict:
    """Декодирует и верифицирует JWT-токен.

    Args:
        token (str): JWT-токен для декодирования.

    Returns:
        dict: Полезная нагрузка токена (payload).

    Raises:
        jwt.JWTError: Если токен недействителен или истек срок его действия.
    """
    public_key = get_public_key()

    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        options={
            "verify_signature": True,
            "verify_aud": False,
            "verify_exp": True
        }
    )
