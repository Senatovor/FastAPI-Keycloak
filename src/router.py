from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.keycloak_api.dependencies import get_cookie_user
from src.keycloak_api.config import config_keycloak
from src.config import templates

router = APIRouter()


@router.get("/")
async def index():
    return RedirectResponse(config_keycloak.keycloak_url)


@router.get("/protected")
async def protected_page(
        user: dict = Depends(get_cookie_user)
):
    return user
