from django.core.exceptions import ValidationError
from django.db import models
from django.http import Http404

from notifications_api_common.viewsets import (
    NotificationCreateMixin,
    NotificationDestroyMixin,
    NotificationMixinBase,
    conditional_atomic,
)
from rest_framework.exceptions import NotAcceptable
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_nested.viewsets import NestedViewSetMixin as _NestedViewSetMixin
from vng_api_common.exceptions import PreconditionFailed
from vng_api_common.geo import (
    DEFAULT_CRS,
    HEADER_ACCEPT,
    HEADER_CONTENT,
    GeoMixin as _GeoMixin,
    extract_header,
)


class NestedViewSetMixin(_NestedViewSetMixin):
    def get_queryset(self):
        """
        catch validation errors if parent_lookup_kwargs have incorrect format
        and return 404
        """
        try:
            queryset = super().get_queryset()
        except ValidationError:
            raise Http404

        return queryset


class GeoMixin(_GeoMixin):
    def perform_crs_negotation(self, request):
        # don't cripple the browsable API...
        if isinstance(request.accepted_renderer, BrowsableAPIRenderer):
            return

        # methods with request bodies need to have the CRS specified
        if request.method.lower() in ("post", "put", "patch"):
            content_crs = extract_header(request, HEADER_CONTENT)
            if content_crs is None:
                raise PreconditionFailed(detail=f"'{HEADER_CONTENT}' header ontbreekt")
            if content_crs != DEFAULT_CRS:
                raise NotAcceptable(detail=f"CRS '{content_crs}' is niet ondersteund")

        if request.method.lower() == "delete":
            return

        # check optional header
        requested_crs = extract_header(request, HEADER_ACCEPT)
        if requested_crs and requested_crs != DEFAULT_CRS:
            raise NotAcceptable(detail=f"CRS '{requested_crs}' is niet ondersteund")


class ObjectNotificationMixinBase(NotificationMixinBase):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if name == "ObjectViewSet":
            kanaal = attrs.get("notifications_kanaal")
            kanaal.usage["object"] = kanaal.usage.pop("objectrecord")

        return new_cls


class ObjectNotificationMixin(
    NotificationCreateMixin,
    NotificationDestroyMixin,
    metaclass=ObjectNotificationMixinBase,
):
    def construct_message(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: dict, instance: models.Model | None = None
    ) -> dict:
        message = super().construct_message(data, instance)  # pyright: ignore[reportAttributeAccessIssue]
        message["resource"] = "object"
        return message

    def update(self, request, *args, **kwargs):
        with conditional_atomic(self.notifications_wrap_in_atomic_block)():
            response = super().update(request, *args, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

            instance = self.get_object()  # pyright: ignore[reportAttributeAccessIssue]
            self.notify(response.status_code, response.data, instance=instance)
            return response
