from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from typing import (
    BinaryIO,
    Callable,
    Iterable,
    Mapping,
    NoReturn,
    Sequence,
)

from django.core.exceptions import SuspiciousFileOperation
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Manager, QuerySet
from django.utils.translation import gettext_lazy as _

import structlog
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BaseSerializer, ModelSerializer

from objects import __version__
from objects.api.serializers import (
    ObjectTypeSerializer as _ObjectTypeSerializer,
    ObjectTypeVersionSerializer as _ObjectTypeVersionSerializer,
)
from objects.core.models import ObjectType, ObjectTypeVersion

logger = structlog.stdlib.get_logger(__name__)


class ObjectTypeVersionSerializer(ModelSerializer[ObjectTypeVersion]):
    class Meta(_ObjectTypeVersionSerializer.Meta):  # type: ignore
        fields = [
            field
            for field in _ObjectTypeVersionSerializer.Meta.fields
            if field not in ["url", "objectType"]  # exclude
        ]
        extra_kwargs = {
            f: kwargs | {"read_only": False}
            for f, kwargs in _ObjectTypeVersionSerializer.Meta.extra_kwargs.items()
        }


class ObjectTypeSerializer(_ObjectTypeSerializer):
    """ObjectTypeSerializer adapted for exporting/importing into a different instance.

    No hyperlinks
    """

    versions = ObjectTypeVersionSerializer(many=True)

    class Meta(_ObjectTypeSerializer.Meta):
        fields = [
            field for field in _ObjectTypeSerializer.Meta.fields if field != "url"
        ]
        extra_kwargs = {
            f: kwargs | {"read_only": False}
            for f, kwargs in _ObjectTypeSerializer.Meta.extra_kwargs.items()
        }

    def create(self, validated_data) -> ObjectType:
        versions = validated_data.pop("versions")
        object_type = super().create(validated_data | {"is_imported": True})
        for data in versions:
            ObjectTypeVersion.objects.create(object_type=object_type, **data)

        return object_type


IMPORT_ORDER: Mapping[str, type[BaseSerializer]] = {
    "objectTypes": ObjectTypeSerializer,
}
EXPORT_MAP = {v: k for k, v in IMPORT_ORDER.items()}


def export_data(
    output: BinaryIO,
    /,
    *,
    objecttypes: Sequence[ObjectType] | QuerySet[ObjectType] | Manager[ObjectType],
) -> None:
    """Export

    The zip will be written to output.
    """

    if isinstance(objecttypes, (QuerySet, Manager)):  # pyright: ignore[reportArgumentType]
        objecttypes = objecttypes.prefetch_related("versions")

    with zipfile.ZipFile(output, "w") as zf:
        zf.writestr(
            _filename(EXPORT_MAP[ObjectTypeSerializer]),
            _encode(
                ObjectTypeSerializer(
                    instance=objecttypes, many=True, context={"request": None}
                ).data
            ),
        )
        zf.writestr(
            "meta.json",
            _encode(_metadata()),
        )


def _strip_uuid(data: object):
    match data:
        case [*members]:
            return [_strip_uuid(m) for m in members]
        case {"uuid": _, **rest}:
            return rest
        case _:  # pragma: no cover
            raise Exception(
                "If you want to reuse this for whatever you're doing, make it recursive"
            )


@transaction.atomic
def import_data(
    export_file: BinaryIO | File, keep_uuid: bool = True
) -> set[str] | NoReturn:
    """Import the data from export_file return the set of resources imported.

    raises
        DRF ValidationError if contents malformed
        zipfile.BadZipFile if file is malformed
    """
    imported_resources: set[str] = set()
    with zipfile.ZipFile(export_file, "r") as zf:
        present = zf.namelist().__contains__

        for resource, Serializer in IMPORT_ORDER.items():
            if not present(_filename(resource)):
                continue

            data = _decode(zf.read(_filename(resource)))

            if not keep_uuid:
                data = _strip_uuid(data)

            serializer = Serializer(data=data, many=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                imported_resources.add(resource)
    return imported_resources


def _flatten_drf_error(error: ValidationError) -> Iterable[str]:
    detail = error.detail
    # DRF >= 3.18 reports list-serializer errors as a dict keyed by (0-based)
    # row index, older versions as a list with one entry per row.
    rows = (
        ((int(index) + 1, item) for index, item in detail.items())
        if isinstance(detail, dict)
        else enumerate(detail, 1)
    )
    return (
        f"Row {index}, {field}: {err}"
        for index, item in rows
        if isinstance(item, dict)
        for field, errors in item.items()
        for err in errors
    )


def import_upload(
    file: UploadedFile | object | list[object],
    keep_uuid: bool,
    report_error_to_user: Callable[[str], None],
) -> set[str]:
    """Import data from Uploaded fiLe and return the set of type names that were imported.

    The object | list[object] annotation doesn't mean you can throw anything at it;
    just anything from request.FILES / form.files, so anything suspicious will raise
    SuspiciousFileOperation
    """
    match file:
        case UploadedFile():
            with file.open() as fd:
                try:
                    return import_data(fd, keep_uuid=keep_uuid)
                except ValidationError as e:
                    for error_msg in _flatten_drf_error(e):
                        report_error_to_user(error_msg)
                except zipfile.BadZipfile:
                    report_error_to_user(
                        _("{file} is not a supported file type").format(file=file.name),
                    )
                except Exception:  # pragma: no cover
                    report_error_to_user(
                        _(
                            "Something unexpected happened during import.\n"
                            "Please try again. If it fails again and you think "
                            "the file should be correct, please include the "
                            "file in your bug report.\n"
                        ).format()
                    )
                    logger.exception("unhandled import exception")
                return set()
        case [*fs]:
            return {
                resource
                for f in fs
                for resource in import_upload(f, keep_uuid, report_error_to_user)
            }
        case _:  # pragma: no cover
            logger.exception("unexected type in upload", contents=file)
            raise SuspiciousFileOperation("Unexpected type in upload")


def _encode(obj: object) -> str:
    return json.dumps(obj, cls=DjangoJSONEncoder)


def _decode(s: bytes | str) -> object:
    return json.loads(s)


def _filename(model_name: str) -> str:
    return f"{model_name}.json"


def _metadata() -> dict[str, str]:
    "Metadata for an export"
    return {
        "app_version": __version__,
        "exported_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
