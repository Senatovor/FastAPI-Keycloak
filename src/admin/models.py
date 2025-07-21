from sqladmin import ModelView

from ..keycloak_api.models import User


class UserAdmin(ModelView, model=User):
    """View-модель пользователя для SQL админки"""
    column_list = [
        User.id,
        User.name,
        User.email,
    ]
    can_create = False
    can_edit = False
    can_delete = False
