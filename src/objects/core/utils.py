from __future__ import annotations

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog
import webcolors
from jsonschema import (
    Draft202012Validator,
    FormatError,
    ValidationError as JSONValidationError,
    draft202012_format_checker,
)
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

from objects.core import models
from objects.typing import JSONObject

logger = structlog.stdlib.get_logger(__name__)


def get_strict_format_checker_default():
    return settings.JSONSCHEMA_USE_FORMAT_CHECKER


@draft202012_format_checker.checks("color")
def is_valid_color(value: str) -> bool:
    """
    Checks if the value is a valid CSS3 color:
        - named CSS3 color
        - hexadecimal color

    Raises FormatError if invalid.
    """
    try:
        webcolors.name_to_hex(value)
    except ValueError:
        try:
            webcolors.hex_to_name(value)
        except ValueError:
            raise FormatError(
                _(
                    "'{value}' is not a valid hexadecimal color and not defined as a named color in CSS3 color".format(
                        value=value
                    )
                )
            )
    return True


@draft202012_format_checker.checks("email")
def is_valid_email(value: str) -> bool:
    """
    Check that 'value' is a reasonably valid email address.

    - Returns False if the value is not a string.
    - Performs a simplified validation.

    """
    pattern = r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
    return bool(re.match(pattern, str(value)))


def validate_jsonschema(
    instance: JSONObject, schema: JSONObject, use_format_checker: bool = True
) -> None:
    """
    Validate ``instance`` against the provided JSON ``schema``.

    :param instance: The JSON object to validate.
    :param schema: The JSON Schema to validate against.
    :param use_format_checker: When ``True``, format constraints are enforced
        using ``draft202012_format_checker``. Defaults to ``True``.
    :raises ValidationError: If ``instance`` does not conform to ``schema``.

    """
    try:
        validator = Draft202012Validator(
            schema,
            format_checker=draft202012_format_checker if use_format_checker else None,
        )
        validator.validate(instance)
    except JSONValidationError as json_error:
        logger.exception("invalid_jsonschema")
        raise ValidationError(json_error.message, code="invalid_jsonschema")


def check_objecttype(
    object_type: "models.ObjectType", version: int, data: JSONObject
) -> None:
    """
    Validate ``data`` against the JSON Schema of a specific ``ObjectType`` version.

    :param object_type: The ``ObjectType`` instance whose version schema to validate against.
    :param version: The version of the ``ObjectTypeVersion`` to use.
    :param data: The JSON object to validate.
    :raises ValidationError: If requested version does not exist.

    """
    try:
        version = object_type.versions.get(version=version)
        validate_jsonschema(
            data, version.json_schema, use_format_checker=version.strict_format_checker
        )
    except models.ObjectTypeVersion.DoesNotExist:
        logger.exception("object_type_version_not_found")
        raise ValidationError(
            f"Object type {object_type} version: {version} does not appear to exist.",
            code="invalid_key",
        )


def check_json_schema(json_schema: dict) -> None:
    """
    Validate that ``json_schema`` is itself a valid JSON Schema.

    :param json_schema: The JSON Schema dict to validate.
    :raises ValidationError: If the schema itself is not a valid JSON Schema.

    """
    schema_validator = validator_for(json_schema)
    try:
        schema_validator.check_schema(json_schema)
    except SchemaError as exc:
        raise ValidationError(exc.message)
