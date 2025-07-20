from ..database.service import BaseService
from .models import User


class UserService(BaseService):
    """Сервис для работы с моделью User в БД"""
    model = User
