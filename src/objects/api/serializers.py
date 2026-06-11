from django.db import transaction
from django.utils.translation import gettext_lazy as _

import structlog
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_gis.serializers import GeometryField
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.utils import get_help_text

from objects.core.models import (
    Object,
    ObjectRecord,
    ObjectType,
    ObjectTypeVersion,
    Reference,
)
from objects.token.models import Permission, TokenAuth
from objects.utils.serializers import DynamicFieldsMixin

from .fields import CachedObjectUrlField, ObjectSlugRelatedField, ObjectTypeField
from .utils import merge_patch
from .validators import (
    GeometryValidator,
    IsImmutableValidator,
    JsonSchemaValidator,
    ObjectTypeSchemaValidator,
    ObjectUUIDUniqueValidator,
    VersionUpdateValidator,
)

logger = structlog.stdlib.get_logger(__name__)


class ObjectTypeVersionSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {"objecttype_uuid": "object_type__uuid"}

    class Meta:
        model = ObjectTypeVersion
        fields = (
            "url",
            "version",
            "objectType",
            "status",
            "jsonSchema",
            "createdAt",
            "modifiedAt",
            "publishedAt",
        )
        extra_kwargs = {
            "url": {"lookup_field": "version"},
            "version": {"read_only": True},
            "objectType": {
                "source": "object_type",
                "lookup_field": "uuid",
                "read_only": True,
            },
            "jsonSchema": {
                "source": "json_schema",
                "validators": [JsonSchemaValidator()],
            },
            "createdAt": {"source": "created_at", "read_only": True},
            "modifiedAt": {"source": "modified_at", "read_only": True},
            "publishedAt": {"source": "published_at", "read_only": True},
        }
        validators = [VersionUpdateValidator()]

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)

        # check parent url
        kwargs = self.context["request"].resolver_match.kwargs
        if not ObjectType.objects.filter(uuid=kwargs["objecttype_uuid"]).exists():
            msg = _("Objecttype url is invalid")
            raise serializers.ValidationError(msg, code="invalid-objecttype")

        return valid_attrs

    def create(self, validated_data):
        kwargs = self.context["request"].resolver_match.kwargs
        object_type = ObjectType.objects.get(uuid=kwargs["objecttype_uuid"])
        validated_data["object_type"] = object_type

        return super().create(validated_data)


@extend_schema_field(
    {
        "type": "object",
        "additionalProperties": {"type": "string"},
    }
)
class LabelsField(serializers.JSONField):
    pass


class ObjectTypeSerializer(serializers.HyperlinkedModelSerializer[ObjectType]):
    labels = LabelsField(
        required=False,
        help_text=get_help_text("core.ObjectType", "labels"),
    )

    versions = NestedHyperlinkedRelatedField(
        many=True,
        read_only=True,
        lookup_field="version",
        view_name="objecttypeversion-detail",
        parent_lookup_kwargs={"objecttype_uuid": "object_type__uuid"},
        help_text=_("list of URLs for the OBJECTTYPE versions"),
    )

    class Meta:
        model = ObjectType
        fields = (
            "url",
            "uuid",
            "name",
            "namePlural",
            "description",
            "dataClassification",
            "maintainerOrganization",
            "maintainerDepartment",
            "contactPerson",
            "contactEmail",
            "source",
            "updateFrequency",
            "providerOrganization",
            "documentationUrl",
            "labels",
            "createdAt",
            "modifiedAt",
            "allowGeometry",
            "versions",
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "uuid": {
                "validators": [
                    IsImmutableValidator(),
                    UniqueValidator(queryset=ObjectType.objects.all()),
                ]
            },
            "namePlural": {"source": "name_plural"},
            "dataClassification": {"source": "data_classification"},
            "maintainerOrganization": {"source": "maintainer_organization"},
            "maintainerDepartment": {"source": "maintainer_department"},
            "contactPerson": {"source": "contact_person"},
            "contactEmail": {"source": "contact_email"},
            "updateFrequency": {"source": "update_frequency"},
            "providerOrganization": {"source": "provider_organization"},
            "documentationUrl": {"source": "documentation_url"},
            "allowGeometry": {"source": "allow_geometry"},
            "createdAt": {"source": "created_at", "read_only": True},
            "modifiedAt": {"source": "modified_at", "read_only": True},
        }


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ["type", "url"]


class ObjectRecordSerializer(serializers.ModelSerializer[ObjectRecord]):
    correctionFor = ObjectSlugRelatedField(
        source="correct",
        slug_field="index",
        required=False,
        allow_null=True,
        help_text=_("Index of the record corrected by the current record"),
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record, which corrects the current record"),
    )
    references = ReferenceSerializer(many=True, read_only=False, default=[])

    class Meta:
        model = ObjectRecord
        fields = (
            "index",
            "typeVersion",
            "data",
            "geometry",
            "references",
            "startAt",
            "endAt",
            "registrationAt",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "index": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startAt": {"source": "start_at"},
            "endAt": {"source": "end_at", "read_only": True},
            "registrationAt": {"source": "registration_at", "read_only": True},
        }


class HistoryRecordSerializer(serializers.ModelSerializer):
    correctionFor = serializers.SlugRelatedField(
        source="correct",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record corrected by the current record"),
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record, which corrects the current record"),
    )

    class Meta:
        model = ObjectRecord
        fields = (
            "index",
            "typeVersion",
            "data",
            "geometry",
            "startAt",
            "endAt",
            "registrationAt",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "index": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startAt": {"source": "start_at"},
            "endAt": {"source": "end_at", "read_only": True},
            "registrationAt": {"source": "registration_at", "read_only": True},
        }


class ObjectSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    url = CachedObjectUrlField(view_name="object-detail")
    uuid = serializers.UUIDField(
        source="object.uuid",
        required=False,
        validators=[
            IsImmutableValidator(),
            ObjectUUIDUniqueValidator(),
        ],
        help_text=_("Unique identifier (UUID4)"),
    )
    type = ObjectTypeField(
        min_length=1,
        max_length=1000,
        source="_object_type",
        help_text=_("Url reference to OBJECTTYPE"),
        validators=[IsImmutableValidator()],
    )
    record = ObjectRecordSerializer(
        source="*", help_text=_("State of the OBJECT at a certain time")
    )

    class Meta:
        model = ObjectRecord
        fields = ("url", "uuid", "type", "record")
        extra_kwargs = {
            "url": {"lookup_field": "object.uuid"},
        }
        validators = [ObjectTypeSchemaValidator(), GeometryValidator()]

    @transaction.atomic
    def create(self, validated_data):
        object_data = validated_data.pop("object", {})

        if object_type := validated_data.pop("_object_type", None):
            object_data["object_type"] = object_type

        object = Object.objects.create(**object_data)

        validated_data["object"] = object
        references = validated_data.pop("references", [])
        record = super().create(validated_data)

        Reference.objects.bulk_create(
            Reference(record=record, **ref_data) for ref_data in references
        )
        token_auth: TokenAuth = self.context["request"].auth
        logger.info(
            "object_created",
            object_uuid=str(object.uuid),
            objecttype_uuid=str(object.object_type.uuid),
            objecttype_version=record.version,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        return record

    @transaction.atomic
    def update(self, instance, validated_data):
        # object_data is not used since all object attributes are immutable
        validated_data.pop("object", None)
        validated_data["object"] = instance.object
        # version should be set
        if "version" not in validated_data:
            validated_data["version"] = instance.version
        # start_at should be set
        if "start_at" not in validated_data:
            validated_data["start_at"] = instance.start_at

        if self.partial:
            # Apply JSON Merge Patch for record data
            validated_data["data"] = merge_patch(
                instance.data, validated_data.pop("data", {})
            )

        references = validated_data.pop(
            "references", instance.references.values("type", "url")
        )
        record = super().create(validated_data)
        Reference.objects.bulk_create(
            Reference(record=record, **ref_data) for ref_data in references
        )
        token_auth: TokenAuth = self.context["request"].auth
        logger.info(
            "object_updated",
            object_uuid=str(record.object.uuid),
            objecttype_uuid=str(record._object_type.uuid),
            objecttype_version=record.version,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        return record


class GeoWithinSerializer(serializers.Serializer):
    within = GeometryField(required=False)


class ObjectSearchSerializer(serializers.Serializer):
    geometry = GeoWithinSerializer(required=False)


class PermissionSerializer(serializers.ModelSerializer):
    type = ObjectTypeField(
        min_length=1,
        max_length=1000,
        source="object_type",
        help_text=_("Url reference to OBJECTTYPE"),
        validators=[IsImmutableValidator()],
    )

    class Meta:
        model = Permission
        fields = ("type", "mode", "use_fields", "fields")
