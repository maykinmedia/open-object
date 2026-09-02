from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers


class HyperlinkedRelatedFieldExtension(OpenApiSerializerFieldExtension):
    target_class = serializers.HyperlinkedRelatedField
    match_subclasses = True

    def map_serializer_field(self, auto_schema, direction):
        schema = build_basic_type(OpenApiTypes.URI)
        assert schema is not None
        schema.update(
            {
                "minLength": 1,
                "maxLength": 1000,
                "description": "URL reference to this object. "
                "This is the unique identification and location of this object.",
            }
        )

        return schema
