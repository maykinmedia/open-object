from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.viewsets import ViewSetMixin
from vng_api_common.permissions import bypass_permissions

from objects.core.models import ObjectRecord, ObjectType
from objects.token.constants import PermissionModes
from objects.token.models import TokenAuth

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class ObjectTypeBasedPermission(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if bypass_permissions(request):
            return True

        # request should be token authenticated
        token = request.auth
        if not isinstance(token, TokenAuth):
            return False

        if token.is_superuser:
            return True

        # detail actions are processed in has_object_permission method
        assert isinstance(view, ViewSetMixin)
        if view.action != "create":
            return True

        data = request.data
        if not isinstance(data, Mapping):
            return False

        object_type_url = data.get("type")
        if not object_type_url:
            return False

        try:
            object_type = ObjectType.objects.get_by_url(object_type_url)  # pyright: ignore[reportAttributeAccessIssue]
        except (ObjectType.DoesNotExist, ValueError, TypeError):
            return False

        object_type_permission = token.get_permission_for_object_type(object_type)
        return bool(
            object_type_permission
            and object_type_permission.mode == PermissionModes.read_and_write
        )

    def has_object_permission(
        self, request: Request, view: APIView, obj: ObjectRecord
    ) -> bool:
        if bypass_permissions(request):
            return True

        token = request.auth
        if not isinstance(token, TokenAuth):
            return False

        if token.is_superuser:
            return True

        object_permission = token.get_permission_for_object_type(obj._object_type)
        if not object_permission:
            return False

        # forbid showing history if there is field based auth
        assert isinstance(view, ViewSetMixin)
        if (
            view.action in ["history", "history_detail"]
            and object_permission.mode == PermissionModes.read_only
            and object_permission.use_fields
        ):
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(object_permission.mode == PermissionModes.read_and_write)


class IsTokenAuthenticated(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.auth)
