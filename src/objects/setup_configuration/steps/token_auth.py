from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models

import structlog
from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed

from objects.core.models import ObjectType
from objects.setup_configuration.models.token_auth import (
    TokenAuthGroupConfigurationModel,
    TokenAuthPermissionConfigurationModel,
)
from objects.token.models import Permission, TokenAuth

logger = structlog.stdlib.get_logger(__name__)


class TokenAuthConfigurationStep(
    BaseConfigurationStep[TokenAuthGroupConfigurationModel]
):
    """
    Configure tokens with permissions for other applications to access Open Object
    """

    namespace = "tokenauth"
    enable_setting = "tokenauth_config_enable"

    verbose_name = "Configuration to set up authentication tokens"
    config_model = TokenAuthGroupConfigurationModel

    def _full_clean(self, instance: models.Model) -> None:
        try:
            instance.full_clean(exclude=("id",), validate_unique=False)
        except ValidationError as exception:
            raise ConfigurationRunFailed(
                ("Validation error(s) during instance cleaning: %s" % type(instance))
            ) from exception

    def _configure_permissions(
        self, token: TokenAuth, permissions: list[TokenAuthPermissionConfigurationModel]
    ) -> None:
        if len(permissions) == 0 and not token.is_superuser:
            logger.warning("no_permissions_defined", token_identifier=token.identifier)

        for permission in permissions:
            try:
                permission_kwargs = {
                    "token_auth": token,
                    "object_type": ObjectType.objects.get(uuid=permission.object_type),
                    "mode": permission.mode,
                }
            except ObjectDoesNotExist as exception:
                raise ConfigurationRunFailed(
                    ("Object type with %s does not exist" % permission.object_type)
                ) from exception

            permission_instance = Permission(**permission_kwargs)
            self._full_clean(permission_instance)

            try:
                Permission.objects.update_or_create(
                    token_auth=permission_kwargs["token_auth"],
                    object_type=permission_kwargs["object_type"],
                    defaults={
                        "mode": permission_kwargs["mode"],
                    },
                )
            except IntegrityError as exception:
                raise ConfigurationRunFailed(
                    (
                        "Failed configuring permission for token %s and object type %s"
                        % (token.identifier, permission.object_type)
                    )
                ) from exception

    def execute(self, model: TokenAuthGroupConfigurationModel) -> None:
        if len(model.items) == 0:
            logger.warning("no_tokens_defined")

        for item in model.items:
            logger.info("configuring_token", token_identifier=item.identifier)

            token_kwargs = {
                "identifier": item.identifier,
                "token": item.token,
                "contact_person": item.contact_person,
                "email": item.email,
                "organization": item.organization,
                "application": item.application,
                "administration": item.administration,
                "is_superuser": item.is_superuser,
            }

            token_instance = TokenAuth(**token_kwargs)
            self._full_clean(token_instance)
            try:
                logger.debug("save_token_to_database", token_identifier=item.identifier)
                token, _ = TokenAuth.objects.update_or_create(
                    identifier=item.identifier,
                    defaults={
                        key: value
                        for key, value in token_kwargs.items()
                        if key != "identifier"
                    },
                )

                self._configure_permissions(token, item.permissions or [])

            except IntegrityError as exception:
                logger.exception(
                    "token_configuration_failure",
                    token_identifier=item.identifier,
                    exc_info=exception,
                )
                raise ConfigurationRunFailed(
                    "Failed configuring token %s" % item.identifier
                ) from exception

            logger.info("token_configuration_success", token_identifier=item.identifier)
