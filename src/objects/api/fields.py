from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.serializers import CachedHyperlinkedIdentityField

from objects.core.models import ObjectRecord, ObjectType


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.select_related(
            "object",
            "object__object_type",
            "correct",
            "corrected",
        ).order_by("-pk")

        record_instance = self.parent.parent.instance
        if not record_instance:
            return queryset.none()

        return queryset.filter(object=record_instance.object)


class ObjectTypeField(serializers.HyperlinkedRelatedField):
    default_error_messages = {
        "max_length": _("The value has too many characters"),
        "min_length": _("The value has too few characters"),
    }

    def __init__(self, **kwargs):
        self.max_length = kwargs.pop("max_length", None)
        self.min_length = kwargs.pop("min_length", None)

        kwargs.setdefault("queryset", ObjectType.objects.all())
        kwargs.setdefault("view_name", "objecttype-detail")
        kwargs.setdefault("lookup_field", "uuid")
        kwargs.setdefault("lookup_url_kwarg", "uuid")

        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.max_length and len(data) > self.max_length:
            self.fail("max_length")

        if self.min_length and len(data) < self.min_length:
            self.fail("min_length")

        return super().to_internal_value(data)


class CachedObjectUrlField(CachedHyperlinkedIdentityField):
    lookup_field = "uuid"

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None
        return super().get_url(obj.object, view_name, request, format)  # pyright: ignore[reportAttributeAccessIssue]
