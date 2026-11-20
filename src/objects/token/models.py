from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _

from objects.core.models import ObjectType
from objects.token.validators import validate_no_empty, validate_no_whitespace

from .constants import PermissionModes

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager


class TokenAuth(models.Model):
    if TYPE_CHECKING:
        permissions: RelatedManager[Permission]

    identifier = models.SlugField(
        unique=True,
        help_text=_("A human-friendly label to refer to this token"),
        validators=[validate_no_empty],
    )
    token = models.CharField(
        _("token"),
        max_length=40,
        unique=True,
        validators=[validate_no_empty, validate_no_whitespace],
    )
    contact_person = models.CharField(
        _("contact person"),
        max_length=200,
        help_text=_("Name of the person in the organization who can access the API"),
    )
    email = models.EmailField(
        _("email"), help_text=_("Email of the person, who can access the API")
    )
    organization = models.CharField(
        _("organization"),
        max_length=200,
        blank=True,
        help_text=_("Organization which has access to the API"),
    )
    last_modified = models.DateTimeField(
        _("last modified"),
        auto_now=True,
        help_text=_("Last date when the token was modified"),
    )
    created = models.DateTimeField(
        _("created"), auto_now_add=True, help_text=_("Date when the token was created")
    )
    application = models.CharField(
        _("application"),
        max_length=200,
        blank=True,
        help_text=_("Application which has access to the API"),
    )
    administration = models.CharField(
        _("administration"),
        max_length=200,
        blank=True,
        help_text=_("Administration which has access to the API"),
    )
    is_superuser = models.BooleanField(
        _("is superuser"),
        default=False,
        help_text=_("Designates whether the user has access to all objects."),
    )

    object_types = models.ManyToManyField(
        "core.ObjectType",
        through="token.Permission",
        help_text=_("Object types which can be accessed"),
    )

    class Meta:
        verbose_name = _("token authorization")
        verbose_name_plural = _("token authorizations")

    def __str__(self):
        return self.identifier

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return secrets.token_hex(20)

    def get_permission_for_object_type(
        self, object_type: ObjectType
    ) -> Permission | None:
        if not self.permissions.filter(object_type=object_type).exists():
            return None
        return self.permissions.get(object_type=object_type)


class Permission(models.Model):
    token_auth = models.ForeignKey(
        "token.TokenAuth", on_delete=models.CASCADE, related_name="permissions"
    )
    object_type = models.ForeignKey(
        "core.ObjectType", on_delete=models.CASCADE, related_name="permissions"
    )
    mode = models.CharField(
        _("mode"),
        max_length=20,
        choices=PermissionModes.choices,
        help_text=_("Permission mode"),
    )
    use_fields = models.BooleanField(
        _("use fields"), default=False, help_text=_("Use field-based authorization")
    )
    fields = models.JSONField(
        _("mode"),
        blank=True,
        null=True,
        default=dict,
        help_text=_(
            "Fields allowed for this token in relation to objecttype versions. "
            "Supports only first level of the `record.data` properties"
        ),
    )

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        unique_together = ("token_auth", "object_type")

    def clean(self):
        if self.mode == PermissionModes.read_and_write and self.use_fields:
            raise exceptions.ValidationError(
                _("Field-based authorization is supported only for read-only mode")
            )
