from functools import wraps

from domain.entities.user import User
from domain.exceptions.auth import UnauthenticatedError, UserBannedError, UserNeedsActivationError


def require_login(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        user = kwargs.get("user")

        if not isinstance(user, User):
            raise UnauthenticatedError("Объект пользователя невалиден или отсутствует.")

        if not user.is_active:
            raise UserNeedsActivationError("Подтвердите почту для активации аккаунта.")

        ban_status = user.ban_status
        if ban_status and ban_status.is_banned:
            if ban_status.is_permanent:
                raise UserBannedError("Пользователь заблокирован бессрочно")
            if ban_status.banned_till:
                raise UserBannedError(f"Пользователь временно заблокирован (до {ban_status.banned_till})")

        return func(self, *args, **kwargs)

    return wrapper
