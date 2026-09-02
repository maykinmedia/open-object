from uuid import UUID

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.plumbing import build_parameter_type, get_view_model
from drf_spectacular.utils import OpenApiParameter
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin
from vng_api_common.constants import VERSION_HEADER
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT
from vng_api_common.schema import HTTP_STATUS_CODE_TITLES

from objects.api.mixins import GeoMixin

from .serializers import DynamicFieldsMixin

object_path_parameter = OpenApiParameter(
    name="object__uuid", required=True, location=OpenApiParameter.PATH
)


class AutoSchema(_AutoSchema):
    def get_response_serializers(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ):
        if self.method == "DELETE":
            return {204: None}

        return super().get_response_serializers()

    def get_operation_id(self):
        """
        Use model name as a base for operation_id
        """
        if isinstance(self.view, GenericViewSet):
            return f"{self.view.basename}_{self.view.action}"
        return super().get_operation_id()

    def get_override_parameters(self):
        """Add request GEO headers"""
        params = super().get_override_parameters()

        geo_headers = self.get_geo_headers()
        content_type_headers = self.get_content_type_headers()
        version_headers = self.get_version_headers()
        parent_path_headers = self.get_parent_path_headers()
        field_params = self.get_fields_params()
        return (
            params
            + geo_headers
            + content_type_headers
            + version_headers
            + parent_path_headers
            + field_params
        )

    def _get_filter_parameters(self):
        """remove filter parameters from all actions except LIST"""
        assert isinstance(self.view, GenericViewSet)
        if self.view.action != "list":
            return []
        return super()._get_filter_parameters()

    def _get_response_for_code(
        self, serializer, status_code, media_types=None, direction="response"
    ):
        """add default description to the response"""
        response = super()._get_response_for_code(
            serializer, status_code, media_types, direction
        )

        if not response.get("description"):
            response["description"] = HTTP_STATUS_CODE_TITLES.get(int(status_code))
        return response

    def get_geo_headers(self) -> list:
        if not isinstance(self.view, GeoMixin):
            return []

        request_headers = []
        if self.method != "DELETE":
            request_headers.append(
                OpenApiParameter(
                    name=HEADER_ACCEPT,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    required=False,
                    description=_(
                        "The desired 'Coordinate Reference System' (CRS) of the response data. "
                        "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                        "is the same as WGS84)."
                    ),
                    enum=[DEFAULT_CRS],
                )
            )

        if self.method in ("POST", "PUT", "PATCH"):
            request_headers.append(
                OpenApiParameter(
                    name=HEADER_CONTENT,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    required=True,
                    description=_(
                        "The 'Coordinate Reference System' (CRS) of the request data. "
                        "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                        "is the same as WGS84)."
                    ),
                    enum=[DEFAULT_CRS],
                ),
            )

        response_headers = [
            OpenApiParameter(
                name=HEADER_CONTENT,
                type=str,
                location=OpenApiParameter.HEADER,
                description=_(
                    "The 'Coordinate Reference System' (CRS) of the request data. "
                    "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                    "is the same as WGS84)."
                ),
                enum=[DEFAULT_CRS],
                response=[200, 201],
            )
        ]

        return request_headers + response_headers

    def get_content_type_headers(self) -> list:
        if self.method not in ["POST", "PUT", "PATCH"]:
            return []

        return [
            OpenApiParameter(
                name="Content-Type",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                enum=["application/json"],
                description=_("Content type of the request body."),
            )
        ]

    def get_version_headers(self) -> list[OpenApiParameter]:
        return [
            OpenApiParameter(
                name=VERSION_HEADER,
                type=str,
                location=OpenApiParameter.HEADER,
                description=_(
                    "Geeft een specifieke API-versie aan in de context van "
                    "een specifieke aanroep. Voorbeeld: 1.2.1."
                ),
                response=True,
            )
        ]

    def get_fields_params(self) -> list[OpenApiParameter]:
        if self.method != "GET":
            return []

        response_serializers = self.get_response_serializers()
        if isinstance(response_serializers, DynamicFieldsMixin):
            return [
                OpenApiParameter(
                    name="fields",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    required=False,
                    description=_(
                        "Comma-separated fields, which should be displayed in the response. "
                        "For example: 'url, uuid, record__geometry'."
                    ),
                ),
                OpenApiParameter(
                    name=settings.UNAUTHORIZED_FIELDS_HEADER,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    response=True,
                    description=_(
                        "List of fields that are not allowed to display if the field-based "
                        "authorization is turned on. The value has the following format: "
                        "`objectType1:fieldA,fieldB; objectType2:fieldC,fieldD`"
                    ),
                ),
            ]

        return []

    def _get_request_body(self, direction="request"):
        """update search request body with filter parameters"""

        assert isinstance(self.view, GenericViewSet)
        request_body = super()._get_request_body(direction)

        if request_body and self.view.action == "search":
            filter_params = self.get_filter_params_for_search()

            properties = {}
            for param in filter_params:
                schema = param["schema"]
                schema["description"] = param["description"]
                properties[param["name"]] = schema

            filter_schema = {"type": "object", "properties": properties}

            for media_type, media_value in request_body["content"].items():
                request_body["content"][media_type]["schema"] = {
                    "type": "object",
                    "allOf": [media_value["schema"], filter_schema],
                }

        return request_body

    def get_filter_params_for_search(self):
        """copy paste of self._get_filter_parameters() without conditions"""
        assert isinstance(self.view, GenericViewSet)
        parameters = []
        for filter_backend in self.view.filter_backends:
            filter_extension = OpenApiFilterExtension.get_match(filter_backend())
            if filter_extension:
                parameters += filter_extension.get_schema_operation_parameters(self)
            else:
                parameters += filter_backend().get_schema_operation_parameters(  # pyright: ignore[reportAttributeAccessIssue]
                    self.view
                )
        return parameters

    def get_parent_path_headers(self) -> list:
        """for nested viewsets"""
        if not isinstance(self.view, NestedViewSetMixin):
            return []

        parent_lookup_kwargs = self.view._get_parent_lookup_kwargs()
        path_params = list(parent_lookup_kwargs.keys())

        return [
            OpenApiParameter(
                name=path_param,
                type=UUID if "uuid" in path_param else str,
                location=OpenApiParameter.PATH,
                required=True,
                description=(
                    _("Unique identifier (UUID4)")
                    if "uuid" in path_param
                    else _("Unique identifier")
                ),
            )
            for path_param in path_params
        ]

    def _resolve_path_parameters(self, variables):
        object_path = "uuid"
        if (
            variables == [object_path]
            and isinstance(self.view, GenericViewSet)
            and self.view.basename == "object"
        ):
            model = get_view_model(self.view)
            assert model is not None
            object_field = model._meta.get_field("object")
            uuid_field = object_field.related_model._meta.get_field("uuid")
            schema = self._map_model_field(uuid_field, direction=None)
            assert schema is not None

            return [
                build_parameter_type(
                    name=object_path, location=OpenApiParameter.PATH, schema=schema
                )
            ]

        return super()._resolve_path_parameters(variables)
