from fastapi import HTTPException, status

NotAccessToken = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Нету access токена авторизации",
)
"""Ошибка при отсутствии access токена"""

InvalidToken = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Недействительный токен'
)
"""Ошибка токена"""

TokenRequestError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Запрос токена не удался"
)
"""Ошибка при запросе токена в keycloak"""

KeycloakRequestError = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Ошибка при запросе к keycloak"
)
"""Ошибка при запросе к keycloak"""

NotCodeError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Требуется код авторизации'
)
"""Ошибка при отсутствии кода авторизации"""

NotFoundUserIdError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='ID пользователя не найден'
)
"""Ошибка при отсутствие ID пользователя в БД приложения"""

AuthError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Ошибка авторизации"
)
"""Ошибка во время авторизации"""
