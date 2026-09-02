from collections import defaultdict
from collections.abc import Mapping

from glom import SKIP, GlomError, glom
from rest_framework import fields, serializers

from objects.tests.v2.utils import reverse
from objects.token.constants import PermissionModes

ALL_FIELDS = ["*"]


def build_spec(fields, ui=False) -> dict:
    spec = {}
    for spec_field in fields:
        build_spec_field(spec, name=spec_field, value=spec_field, ui=ui)
    return spec


def build_spec_field(spec, name, value, ui):
    if "__" in name:
        parent, field_name = name.split("__", 1)
        spec[parent] = spec.get(parent, {})
        build_spec_field(spec[parent], field_name, value, ui)
    else:
        # SKIP data attributes which are not required
        spec_val = (
            value.replace("__", ".")
            if not value.startswith("record__data__")
            else lambda x: glom(x, value.replace("__", "."), default=SKIP)
        )
        spec[name] = value if ui else spec_val


def get_field_names(data: Mapping[str, fields.Field]) -> list[str]:
    """return list of names for all serializer fields. Supports nesting"""
    names_and_sources = get_field_names_and_sources(data)
    return [name for name, source in names_and_sources]


def get_field_names_and_sources(
    data: Mapping[str, fields.Field],
) -> list[tuple[str, str]]:
    """return list of (name, source) for all serializer fields. Supports nesting"""
    names_and_sources = []
    for key, value in data.items():
        if isinstance(value, dict):
            names_and_sources += [
                (f"{key}__{name}", source.replace(".", "__"))
                for name, source in get_field_names_and_sources(value)
            ]
        elif isinstance(value, serializers.Serializer):
            names_and_sources += [
                (f"{key}__{name}", source.replace(".", "__"))
                for name, source in get_field_names_and_sources(value.fields)
            ]
        elif isinstance(value, fields.Field):
            source = value.source or key
            names_and_sources.append((key, source.replace(".", "__")))
        else:
            names_and_sources.append((key, key))

    return names_and_sources


class NotAllowedDict(defaultdict):
    def pretty(self):
        if len(self.keys()) == 0:
            return ""
        if len(self.keys()) == 1:
            value = list(self.values())[0]
            return ",".join(value)
        return "; ".join([f"{key}={','.join(value)}" for (key, value) in self.items()])


class DynamicFieldsMixin:
    """
    this mixin allows selecting fields for serializer in the query param
    It also supports nested fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.not_allowed = NotAllowedDict(set)

    def to_representation(self, instance):
        data = super().to_representation(instance)  # type: ignore[reportAttributeAccessIssue]

        allowed_fields = self.get_allowed_fields(instance)
        query_fields = self.get_query_fields()

        if not query_fields and allowed_fields == ALL_FIELDS:
            return data

        #  limit all data to the allowed
        if allowed_fields == ALL_FIELDS:
            allowed_data = data
        else:
            spec_allowed = build_spec(allowed_fields)
            try:
                allowed_data = glom(data, spec_allowed)
            except GlomError as exc:
                raise serializers.ValidationError(
                    f"Fields in the configured authorization are absent in the data: {exc.args[0]}"
                )

        #  limit allowed data to requested in fields= query param
        if not query_fields:
            result_data = allowed_data
            not_allowed = set(get_field_names(data)) - set(get_field_names(result_data))
            if not_allowed:
                self.not_allowed[
                    f"{
                        self.context['request'].build_absolute_uri(  # type: ignore[reportAttributeAccessIssue]
                            reverse(
                                'objecttype-detail', args=[instance._object_type.uuid]
                            )
                        )
                    }({instance.version})"
                ] |= not_allowed
        else:
            spec_query = build_spec(query_fields)
            try:
                result_data = glom(allowed_data, spec_query)
            except GlomError as exc:
                raise serializers.ValidationError(
                    f"'fields' query parameter has invalid or unauthorized values: {exc.args[0]}"
                )
            not_allowed = set(get_field_names(glom(data, spec_query))) - set(
                get_field_names(result_data)
            )
            if not_allowed:
                self.not_allowed[
                    f"{
                        self.context['request'].build_absolute_uri(  # type: ignore[reportAttributeAccessIssue]
                            reverse(
                                'objecttype-detail', args=[instance._object_type.uuid]
                            )
                        )
                    }({instance.version})"
                ] |= not_allowed

        return result_data

    def get_query_fields(self) -> list:
        request = self.context.get("request")  # type: ignore[reportAttributeAccessIssue]
        if not request:
            return []

        fields = request.query_params.get("fields")
        if not fields:
            return []

        return list({field.strip() for field in fields.split(",")})

    def get_allowed_fields(self, instance) -> list:
        request = self.context.get("request")  # type: ignore[reportAttributeAccessIssue]

        # if not instance -> create or update -> all fields are allowed
        if not request:
            return ALL_FIELDS

        if request.auth.is_superuser:
            return ALL_FIELDS

        # use prefetch_related for DB optimization
        if getattr(instance._object_type, "token_permissions", None):
            permission = instance._object_type.token_permissions[0]
        else:
            permission = request.auth.get_permission_for_object_type(
                instance._object_type
            )
        if permission.mode == PermissionModes.read_only and permission.use_fields:
            return permission.fields.get(str(instance.version), [])

        return ALL_FIELDS
