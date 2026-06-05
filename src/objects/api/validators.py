from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import get_attribute

from objects.core.models import Object
from objects.core.utils import check_json_schema, check_objecttype

from ..core.constants import ObjectTypeVersionStatus
from .constants import Operators
from .utils import merge_patch, string_to_value


class ObjectUUIDUniqueValidator:
    """
    Validate that the UUID is unique, but only on create.

    On update, the IsImmutableValidator ensures the UUID doesn't change,
    so we don't need to check uniqueness (and the standard UniqueValidator
    can't properly exclude the current instance because the serializer's
    instance is an ObjectRecord, not an Object).
    """

    message = _("An object with this UUID already exists.")
    code = "unique"
    requires_context = True

    def __call__(self, value, serializer_field):
        instance = getattr(serializer_field.parent, "instance", None)
        # no instance -> it's a create, check uniqueness
        if instance is not None:
            return

        if Object.objects.filter(uuid=value).exists():
            raise serializers.ValidationError(self.message, code=self.code)


class VersionUpdateValidator:
    message = _("Only draft versions can be changed")
    code = "non-draft-version-update"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)
        if not instance:
            return

        if instance.status != ObjectTypeVersionStatus.draft:
            raise serializers.ValidationError(self.message, code=self.code)


class JsonSchemaValidator:
    code = "invalid-json-schema"

    def __call__(self, value):
        try:
            check_json_schema(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc


class ObjectTypeSchemaValidator:
    code = "invalid-json-schema"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)

        # create
        if not instance:
            object_type = attrs.get("_object_type")
            version = attrs.get("version")
            data = attrs.get("data", {})

        # update
        else:
            object_type = (
                attrs.get("_object_type")
                if "_object_type" in attrs
                else instance._object_type
            )
            version = attrs.get("version") if "version" in attrs else instance.version
            data = attrs.get("data", {}) if "data" in attrs else instance.data
            if serializer.partial and "data" in attrs:
                # Apply JSON Merge Patch for record data
                data = merge_patch(instance.data, attrs["data"])

        if not object_type or not version:
            return
        try:
            check_objecttype(object_type, version, data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc


class IsImmutableValidator:
    """
    Validate that the field should not be changed in update action
    """

    message = _("This field can't be changed")
    code = "immutable-field"
    requires_context = True

    def __call__(self, new_value, serializer_field):
        instance = getattr(serializer_field.parent, "instance", None)
        # no instance -> it's not an update
        if not instance:
            return

        current_value = get_attribute(instance, serializer_field.source_attrs)

        if new_value != current_value:
            raise serializers.ValidationError(self.message, code=self.code)


def validate_data_attr_value_part(value_part: str, code: str):
    try:
        variable, operator, val = value_part.rsplit("__", 2)
    except ValueError:
        message = _(
            "Filter expression '%(value_part)s' doesn't have the shape 'key__operator__value'"
        ) % {"value_part": value_part}
        raise serializers.ValidationError(message, code=code)

    if operator not in Operators.values:
        message = _("Comparison operator `%(operator)s` is unknown") % {
            "operator": operator
        }
        raise serializers.ValidationError(message, code=code)

    if operator not in (
        Operators.exact,
        Operators.icontains,
        Operators.in_list,
    ) and isinstance(string_to_value(val), str):
        message = _(
            "Operator `%(operator)s` supports only dates and/or numeric values"
        ) % {"operator": operator}
        raise serializers.ValidationError(message, code=code)


def validate_data_attrs(value: str):
    # todo remove when 'data_attrs' filter is removed
    code = "invalid-data-attrs-query"
    parts = value.split(",")

    for value_part in parts:
        validate_data_attr_value_part(value_part, code)


def validate_data_attr(value: list):
    code = "invalid-data-attr-query"

    for value_part in value:
        # check that comma can be only in the value part
        if "," in value_part.rsplit("__", 1)[0]:
            message = _(
                "Filter expression '%(value_part)s' must have the shape 'key__operator__value', "
                "commas can only be present in the 'value'"
            ) % {"value_part": value_part}
            raise serializers.ValidationError(message, code=code)

        validate_data_attr_value_part(value_part, code)


class GeometryValidator:
    code = "geometry-not-allowed"
    message = _("This object type doesn't support geometry")
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)
        object_type = attrs.get("_object_type") or instance._object_type
        geometry = attrs.get("geometry")

        if not geometry:
            return

        if geometry and not object_type.allow_geometry:
            raise serializers.ValidationError(self.message, code=self.code)
