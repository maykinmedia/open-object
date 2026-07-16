import datetime

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

import structlog
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from notifications_api_common.cloudevents import process_cloudevent
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from vng_api_common.filters_backend import Backend as FilterBackend
from vng_api_common.pagination import DynamicPageSizePagination
from vng_api_common.search import SearchMixin

from objects.api.metrics import (
    objecttype_create_counter,
    objecttype_delete_counter,
    objecttype_update_counter,
)
from objects.cloud_events.constants import ZAAK_ONTKOPPELD
from objects.cloud_events.tasks import send_zaak_events
from objects.core.constants import ObjectTypeVersionStatus, ReferenceType
from objects.core.models import Object, ObjectRecord, ObjectType, ObjectTypeVersion
from objects.token.authentication import TokenAuthentication
from objects.token.models import Permission, TokenAuth
from objects.token.permissions import IsTokenAuthenticated, ObjectTypeBasedPermission

from ..filter_backends import OrderingBackend
from ..kanalen import KANAAL_OBJECTEN
from ..metrics import (
    objects_create_counter,
    objects_delete_counter,
    objects_update_counter,
)
from ..mixins import GeoMixin, NestedViewSetMixin, ObjectNotificationMixin
from ..serializers import (
    HistoryRecordSerializer,
    ObjectSearchSerializer,
    ObjectSerializer,
    ObjectTypeSerializer,
    ObjectTypeVersionSerializer,
    PermissionSerializer,
)
from ..utils import is_date
from .filters import (
    DATA_ATTR_HELP_TEXT,
    DATA_ATTRS_HELP_TEXT,
    ObjectRecordFilterSet,
    ObjectTypeFilterSet,
)

logger = structlog.stdlib.get_logger(__name__)

# manually override OAS because of "deprecated" attribute
data_attrs_parameter = OpenApiParameter(
    name="data_attrs",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description=DATA_ATTRS_HELP_TEXT,
    deprecated=True,
)

# manually override OAS because of "explode" attribute
data_attr_parameter = OpenApiParameter(
    name="data_attr",
    location=OpenApiParameter.QUERY,
    type=OpenApiTypes.STR,
    description=DATA_ATTR_HELP_TEXT,
    explode=True,
)

logger = structlog.stdlib.get_logger(__name__)


@extend_schema_view(
    retrieve=extend_schema(operation_id="objecttype_read"),
    destroy=extend_schema(operation_id="objecttype_delete"),
)
class ObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = ObjectType.objects.prefetch_related("versions").order_by("-pk")
    serializer_class = ObjectTypeSerializer
    lookup_field = "uuid"
    filterset_class = ObjectTypeFilterSet
    pagination_class = DynamicPageSizePagination
    permission_classes = [IsTokenAuthenticated]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        obj = serializer.instance
        token_auth: TokenAuth = self.request.auth
        logger.info(
            "objecttype_created",
            uuid=str(obj.uuid),
            name=obj.name,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        objecttype_create_counter.add(1)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        obj = serializer.instance
        token_auth: TokenAuth = self.request.auth
        logger.info(
            "objecttype_updated",
            uuid=str(obj.uuid),
            name=obj.name,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        objecttype_update_counter.add(1)

    def perform_destroy(self, instance):
        if instance.versions.exists():
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        _(
                            "All related versions should be destroyed before destroying the objecttype"
                        )
                    ]
                },
                code="pending-versions",
            )

        super().perform_destroy(instance)
        token_auth: TokenAuth = self.request.auth
        logger.info(
            "objecttype_deleted",
            uuid=str(instance.uuid),
            name=instance.name,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        objecttype_delete_counter.add(1)


@extend_schema_view(
    retrieve=extend_schema(
        operation_id="objecttypeversion_read",
        description=_("Retrieve an OBJECTTYPE with the given version."),
    ),
    list=extend_schema(
        operation_id="objecttypeversion_list",
        description=_("Retrieve all versions of an OBJECTTYPE"),
    ),
    create=extend_schema(
        operation_id="objecttypeversion_create",
        description=_("Create an OBJECTTYPE with the given version."),
    ),
    destroy=extend_schema(
        operation_id="objecttypeversion_delete",
        description=_("Destroy the given OBJECTTYPE."),
    ),
    update=extend_schema(
        operation_id="objecttypeversion_update",
        description=_("Update an OBJECTTYPE with the given version."),
    ),
    partial_update=extend_schema(
        operation_id="objecttypeversion_partial_update",
        description=_("Partially update an OBJECTTYPE with the given version."),
    ),
)
class ObjectTypeVersionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = ObjectTypeVersion.objects.order_by("object_type", "-version")
    serializer_class = ObjectTypeVersionSerializer
    lookup_field = "version"
    pagination_class = DynamicPageSizePagination

    def get_authenticators(self):
        request = getattr(self, "request", None)

        if request and request.method in ("GET", "HEAD", "OPTIONS"):
            return [
                SessionAuthentication(),
                TokenAuthentication(),
            ]

        return [TokenAuthentication()]

    def get_permissions(self):
        request = self.request

        if request and request.method in ("GET", "HEAD", "OPTIONS"):
            permission_class = IsAuthenticated | IsTokenAuthenticated
        else:
            permission_class = IsTokenAuthenticated

        return [permission_class()]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        obj = serializer.instance
        token_auth = self.request.auth
        logger.info(
            "object_version_created",
            version=str(obj.version),
            objecttype_uuid=str(obj.object_type.uuid),
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        obj = serializer.instance
        token_auth = self.request.auth
        logger.info(
            "object_version_updated",
            version=str(obj.version),
            objecttype_uuid=str(obj.object_type.uuid),
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )

    def perform_destroy(self, instance):
        if instance.status != ObjectTypeVersionStatus.draft:
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        _("Only draft versions can be destroyed")
                    ]
                },
                code="non-draft-version-destroy",
            )

        super().perform_destroy(instance)
        token_auth = self.request.auth
        logger.info(
            "object_version_deleted",
            version=str(instance.version),
            objecttype_uuid=str(instance.object_type.uuid),
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of OBJECTs and their actual RECORD. "
        "The actual record is defined as if the query parameter `date=<today>` was given.",
        parameters=[data_attrs_parameter, data_attr_parameter],
    ),
    retrieve=extend_schema(
        description="Retrieve a single OBJECT and its actual RECORD. "
        "The actual record is defined as if the query parameter `date=<today>` was given.",
        operation_id="object_read",
    ),
    create=extend_schema(description="Create an OBJECT and its initial RECORD."),
    update=extend_schema(
        description="Update the OBJECT by creating a new RECORD with the updates values."
    ),
    partial_update=extend_schema(
        description="Update the OBJECT by creating a new RECORD with the updates values. "
        "The provided `record.data` value will be merged recursively with the existing record data."
    ),
    destroy=extend_schema(
        description="Delete an OBJECT and all RECORDs belonging to it.",
        operation_id="object_delete",
        parameters=[
            OpenApiParameter(
                name="zaak",
                description=(
                    "**Experimental** When destructing for archiving a ztc.ZAAK "
                    "pass in the ZAAK URL that is being destroyed. "
                    "If this OBJECT's current RECORD has other ZAAK references, "
                    "then object destruction is cancelled "
                    "and only this ZAAK URL is removed from the RECORD's references."
                ),
                type=OpenApiTypes.URI,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="OBJECT kept because it has multiple ZAKEN. Specified ZAAK parameter removed from RECORD.",
                response=inline_serializer(
                    name="BehoudenResponse",
                    fields={
                        "behouden": serializers.ListField(
                            child=serializers.URLField(), help_text="Kept OBJECT URLs"
                        )
                    },
                ),
            ),
            204: OpenApiResponse(description="OBJECT and all its RECORDs deleted."),
        },
    ),
)
class ObjectViewSet(
    ObjectNotificationMixin, SearchMixin, GeoMixin, viewsets.ModelViewSet
):
    queryset = (
        ObjectRecord.objects.select_related(
            "_object_type",
            "correct",
            "corrected",
        )
        .prefetch_related("object", "references")
        .order_by("-pk")
    )
    serializer_class = ObjectSerializer
    filterset_class = ObjectRecordFilterSet
    filter_backends = [FilterBackend, OrderingBackend]
    ordering_fields = "__all__"
    json_field = "record__data"
    lookup_field = "object__uuid"
    lookup_url_kwarg = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    permission_classes = [ObjectTypeBasedPermission]
    pagination_class = DynamicPageSizePagination
    notifications_kanaal = KANAAL_OBJECTEN

    def get_queryset(self):
        base = super().get_queryset()
        token_auth = getattr(self.request, "auth", None)
        # prefetch permissions for DB optimization. Used in DynamicFieldsMixin
        base = base.prefetch_related(
            models.Prefetch(
                "_object_type__permissions",
                queryset=Permission.objects.filter(token_auth=token_auth),
                to_attr="token_permissions",
            ),
        )

        if self.action not in ("list", "search"):
            return base

        # show only allowed objects
        base = base.filter_for_token(token_auth)
        return base

    def filter_queryset(self, queryset):
        # show only actual objects
        if self.action in ("list", "search", "retrieve"):
            date = getattr(self.request, "query_params", {}).get("date", None)
            registration_date = getattr(self.request, "query_params", {}).get(
                "registrationDate", None
            )

            if date and is_date(date):
                queryset = queryset.filter_for_date(parse_date(date))
            elif registration_date and is_date(registration_date):
                queryset = queryset.filter_for_registration_date(
                    parse_date(registration_date)
                )
            else:
                queryset = queryset.filter_for_date(datetime.date.today())

        # keep only records with max index per object
        queryset = queryset.keep_max_record_per_object()

        # filter on the rest of query params
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        objects_create_counter.add(1)

        if record := serializer.instance:
            object_path = reverse(
                "v2:object-detail", kwargs={"uuid": str(record.object.uuid)}
            )
            object_url = self.request.build_absolute_uri(object_path)
            send_zaak_events.delay(record.pk, object_url)
        else:
            logger.warning("missing_record")  # will this happen?

    def perform_update(self, serializer):
        super().perform_update(serializer)
        objects_update_counter.add(1)

        if record := serializer.instance:
            object_path = reverse(
                "v2:object-detail", kwargs={"uuid": str(record.object.uuid)}
            )
            object_url = self.request.build_absolute_uri(object_path)
            send_zaak_events.delay(record.pk, object_url)
        else:
            logger.warning("missing_record")  # will this happen?

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        notification_data = self.get_serializer(instance).data
        obj: Object = instance.object

        object_path = reverse("v2:object-detail", kwargs={"uuid": str(obj.uuid)})
        object_url = self.request.build_absolute_uri(object_path)
        zaak_references = obj.last_record.references.filter(type=ReferenceType.zaak)

        match settings.ENABLE_CLOUD_EVENTS and list(
            zaak_references.values_list("url", flat=True)
        ):
            case [*zaak_urls] if (
                archiving_zaak_url := request.query_params.get("zaak")
            ) and len(zaak_urls) > 1:
                # OAB is archiving one of many ZAKEN attached to this object;
                # just remove this single zaak reference; don't delete the object
                zaak_references.filter(url=archiving_zaak_url).delete()
                process_cloudevent(
                    ZAAK_ONTKOPPELD,
                    data={
                        "zaak": archiving_zaak_url,
                        "linkTo": object_url,
                        "linkObjectType": "object",
                    },
                )

                response = Response(
                    {"behouden": [object_url]}, status=status.HTTP_200_OK
                )
                self.action = "update"  # change action for notification
                self.notify(response.status_code, notification_data, instance=instance)
                return response

            case [*zaak_urls] if zaak_urls:

                def send_events():
                    for zaak_url in zaak_urls:
                        process_cloudevent(
                            ZAAK_ONTKOPPELD,
                            data={
                                "zaak": zaak_url,
                                "linkTo": object_url,
                                "linkObjectType": "object",
                            },
                        )

                transaction.on_commit(send_events)

        obj.delete()
        objects_delete_counter.add(1)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.notify(response.status_code, notification_data, instance=instance)
        return response

    @extend_schema(
        description="Retrieve all RECORDs of an OBJECT.",
        responses={"200": HistoryRecordSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], serializer_class=HistoryRecordSerializer)
    def history(self, request, uuid=None):
        """Retrieve all RECORDs of an OBJECT."""
        records = self.get_object().object.records.order_by("id")

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Retrieve the specified OBJECT given an UUID and INDEX.",
        responses={"200": HistoryRecordSerializer()},
        parameters=[
            OpenApiParameter(
                name="index",
                location=OpenApiParameter.PATH,
                required=True,
                type=OpenApiTypes.NUMBER,
            ),
            OpenApiParameter(
                name="uuid",
                location=OpenApiParameter.PATH,
                required=True,
                type=OpenApiTypes.UUID,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["get"],
        url_path=r"(?P<index>\d+)",
        serializer_class=HistoryRecordSerializer,
    )
    def history_detail(self, request, uuid=None, index=None):
        """Retrieve a RECORD of an OBJECT."""
        queryset = self.get_queryset()
        record = get_object_or_404(queryset, object__uuid=uuid, index=index)
        self.check_object_permissions(self.request, record)
        serializer = self.get_serializer(record)
        return Response(serializer.data)

    @extend_schema(
        description="Perform a (geo) search on OBJECTs.",
        request=ObjectSearchSerializer,
        responses={"200": ObjectSerializer(many=True)},
    )
    @action(detail=False, methods=["post"])
    def search(self, request):
        """Perform a (geo) search on OBJECTs"""
        search_input = self.get_search_input()
        queryset = self.filter_queryset(self.get_queryset())

        if "geometry" in search_input:
            within = search_input["geometry"]["within"]
            queryset = queryset.filter(geometry__within=within).distinct()

        return self.get_search_output(queryset)

    def get_search_output(self, queryset: models.QuerySet) -> Response:
        """wrapper to make sure the result is a Response subclass"""
        result = super().get_search_output(queryset)

        if not isinstance(result, Response):
            result = Response(result)

        return result

    # for OAS generation
    search.is_search_action = True

    def finalize_response(self, request, response, *args, **kwargs):
        """add warning header if not all data is allowed to display"""

        if response.status_code == 200:
            serializer = getattr(response.data, "serializer", None) or getattr(
                response.data.get("results"), "serializer", None
            )
            if self.action == "retrieve" and serializer.not_allowed:
                self.headers[settings.UNAUTHORIZED_FIELDS_HEADER] = (
                    serializer.not_allowed.pretty()
                )

            elif self.action in ("list", "search") and serializer.child.not_allowed:
                self.headers[settings.UNAUTHORIZED_FIELDS_HEADER] = (
                    serializer.child.not_allowed.pretty()
                )

        return super().finalize_response(request, response, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of permissions available for the user"
    )
)
class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.select_related("object_type", "token_auth").order_by(
        "object_type"
    )
    serializer_class = PermissionSerializer
    lookup_field = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    pagination_class = DynamicPageSizePagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # show permissions for the current user
        return queryset.filter(token_auth=self.request.auth)
