from pydantic import BaseModel


class UserId(BaseModel):
    """Модель для ID пользователя"""
    user_id: str


class User(BaseModel):
    """Модель Юзера"""
    email: str
    name: str
    preferred_username: str
    given_name: str
    family_name: str


class AddUser(User):
    """Модель для добавления Юзера"""
    id: str
    email_verified: bool
