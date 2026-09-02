from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from vng_api_common.exception_handling import register_exception_handler


def jsonpath_database_error_handler(exc, context):
    """
    Handle DatabaseError raised when PostgreSQL cannot execute jsonpath queries.
    """

    if "jsonpath" not in str(exc):
        return None

    exc.detail = ErrorDetail(
        str(_("This search operation is not supported by the underlying data store.")),
        code="search-not-supported",
    )
    exc.default_detail = _("Internal Server Error")
    return Response(
        data={"detail": exc.detail},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_handlers():
    from django.db.utils import Error

    register_exception_handler(Error, jsonpath_database_error_handler)  # type: ignore[reportArgumentType]
