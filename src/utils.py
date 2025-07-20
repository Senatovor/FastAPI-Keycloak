from fastapi import HTTPException, status


def ok_response_docs(
        description: str | None = None,
        status_code: int = status.HTTP_200_OK,
) -> dict:
    """Генерирует документацию для положительных ответов в формате OpenAPI.

    Args:
        status_code: Статус ответа
        description: Описание ошибки для документации

    Returns:
        Словарь с описанием ошибки в формате OpenAPI
    """
    return {
        status_code: {
            "description": description,
        }
    }


def error_response_docs(
        error: HTTPException,
        description: str | None = None,
) -> dict:
    """Генерирует документацию для ошибок в формате OpenAPI.

    Args:
        error: Исключение HTTPException
        description: Описание ошибки для документации

    Returns:
        Словарь с описанием ошибки в формате OpenAPI
    """
    return {
        error.status_code: {
            "description": description or error.detail,
            "content": {
                "application/json": {
                    "example": {
                        "detail": error.detail,
                        **({"headers": error.headers} if error.headers else {})
                    }
                }
            }
        }
    }


def tag_metadata(
        tag: str,
        description: str
) -> dict:
    """Генерирует документацию для тэгов в формате OpenAPI.

    Args:
        tag: Имя тэга
        description: Описание тэга для документации

    Returns:
        Словарь с описанием тэга в формате OpenAPI
    """
    return {
        "name": tag,
        "description": description,
    }
