from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import check_password
from django.http import HttpRequest


class UserModelEmailBackend(ModelBackend):
    """
    Authentication backend for login with email address.
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: object,
    ) -> AbstractBaseUser | None:
        try:
            user = get_user_model().objects.get(email__iexact=username, is_active=True)
            if check_password(password, user.password):
                return user
        except get_user_model().DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None
