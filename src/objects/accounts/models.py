from __future__ import annotations

from datetime import date, datetime
from typing import ClassVar, Self

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.db.models.expressions import Combinable
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username = models.CharField[str, str](
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer."),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField[str, str](_("first name"), max_length=255, blank=True)
    last_name = models.CharField[str, str](_("last name"), max_length=255, blank=True)
    email = models.EmailField[str, str](_("email address"), blank=True)
    is_staff = models.BooleanField[bool, bool](
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField[bool | Combinable, bool](
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField[datetime | date | str, datetime](
        _("date joined"), default=timezone.now
    )

    objects: ClassVar[UserManager[Self]] = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: ClassVar[list[str]] = ["email"]

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            models.UniqueConstraint(
                fields=["email"], condition=~Q(email=""), name="filled_email_unique"
            )
        ]

    def get_full_name(self) -> str:
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "{} {}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self) -> str:
        "Returns the short name for the user."
        return self.first_name
