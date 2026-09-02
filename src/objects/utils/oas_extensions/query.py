from drf_spectacular.contrib.django_filters import (
    DjangoFilterExtension as _DjangoFilterExtension,
)
from drf_spectacular.plumbing import build_basic_type, build_parameter_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from vng_api_common import filters_backend

from ..filters import ObjectTypeFilter


class DjangoFilterExtension(_DjangoFilterExtension):
    target_class = filters_backend.Backend
    priority = 1

    def resolve_filter_field(
        self, auto_schema, model, filterset_class, field_name, filter_field
    ):
        """
        Generate proper OAS for ObjectTypeFilter
        """
        if isinstance(filter_field, ObjectTypeFilter):
            schema = build_basic_type(OpenApiTypes.URI)
            assert schema is not None
            if "max_length" in filter_field.extra:
                schema["maxLength"] = filter_field.extra.get("max_length")
            if "min_length" in filter_field.extra:
                schema["minLength"] = filter_field.extra["min_length"]

            description = filter_field.extra["help_text"]

            return [
                build_parameter_type(
                    name=field_name,
                    required=filter_field.extra["required"],
                    location=OpenApiParameter.QUERY,
                    description=description,
                    schema=schema,
                )
            ]
        return super().resolve_filter_field(
            auto_schema, model, filterset_class, field_name, filter_field
        )
