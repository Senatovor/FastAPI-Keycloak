from sqlalchemy.orm import Mapped, mapped_column

from ..database.model import Base


class User(Base):
    """ORM-модель пользователя системы.

    Attributes:
        email: Электронная почта пользователя. Должна быть уникальной.
        email_verified: Верификация почты.
        name: Имя-Фамилия пользователя
        preferred_username: Логин пользователя.
        given_name: Имя пользователя.
        family_name: Фамилия пользователя.
    """
    email: Mapped[str] = mapped_column(unique=True)
    email_verified: Mapped[bool]
    name: Mapped[str]
    preferred_username: Mapped[str]
    given_name: Mapped[str]
    family_name: Mapped[str]
