from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import gettext as _

from djangorestframework_camel_case.util import camel_to_underscore
from packaging.version import Version
from requests.exceptions import RequestException
from zgw_consumers.models import Service

from objects.core.models import ObjectType, ObjectTypeVersion
from objects.utils.client import get_objecttypes_client


def _underscoreize_keys(data: dict[str, object]) -> dict[str, object]:
    "Underscoreize only top-level keys, leaving values untouched."

    # This will break on nested serialisations like "_expand", but this API
    # has none of those. And if it does, hypothesis will show it in time.

    return {camel_to_underscore(k): v for k, v in data.items()}


# Minimum Objecttypes application version is 3.4.0, because that version added the
# version header to the responses
MIN_OBJECTTYPES_API_VERSION = "2.2.2"


class Command(BaseCommand):
    help = "Import ObjectTypes & ObjectTypeVersions from an Objecttypes API based on the service identifier."

    def add_arguments(self, parser):
        parser.add_argument(
            "service_slug",
            help=_("Identifier/slug of Objecttypes API service"),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        service_slug = options["service_slug"]
        service = self._get_service(service_slug)

        with get_objecttypes_client(service) as client:
            try:
                self._check_objecttypes_api_version(client)

                objecttypes = client.list_objecttypes()
                data = self._parse_objecttype_data(objecttypes)
                self._bulk_create_or_update_objecttypes(data)
                self.stdout.write("Successfully imported %s objecttypes" % len(data))

                for objecttype in data:
                    objecttype_versions = client.list_objecttype_versions(
                        objecttype.uuid
                    )
                    data = self._parse_objecttypeversion_data(
                        objecttype_versions, objecttype
                    )
                    self._bulk_create_or_update_objecttype_versions(data)
                    self.stdout.write(
                        "Successfully imported %s versions for type: %s"
                        % (len(data), objecttype.name)
                    )

            except RequestException as e:
                raise CommandError(
                    _(
                        "Something went wrong while making requests to Objecttypes API: {}"
                    ).format(e)
                )

    def _get_service(self, slug):
        try:
            return Service.objects.get(slug=slug)
        except Service.DoesNotExist:
            raise CommandError(_("Service '{}' does not exist").format(slug))

    def _check_objecttypes_api_version(self, client):
        api_version = client.get_objecttypes_api_version()
        if api_version is None or Version(
            client.get_objecttypes_api_version()
        ) < Version(MIN_OBJECTTYPES_API_VERSION):
            raise CommandError(
                _("Object types API version must be {} or higher.").format(
                    MIN_OBJECTTYPES_API_VERSION
                )
            )

    def _bulk_create_or_update_objecttypes(self, data):
        ObjectType.objects.bulk_create(
            data,
            update_conflicts=True,  # Updates existing Objecttypes based on unique_fields
            unique_fields=[
                "uuid",
            ],
            update_fields=[
                "is_imported",
                "name",
                "name_plural",
                "description",
                "data_classification",
                "maintainer_organization",
                "maintainer_department",
                "contact_person",
                "contact_email",
                "source",
                "update_frequency",
                "provider_organization",
                "documentation_url",
                "labels",
                "created_at",
                "modified_at",
                "allow_geometry",
            ],
        )

    def _bulk_create_or_update_objecttype_versions(self, data):
        ObjectTypeVersion.objects.bulk_create(
            data,
            ignore_conflicts=True,
            unique_fields=[
                "object_type",
                "version",
            ],
            update_fields=[
                "created_at",
                "modified_at",
                "published_at",
                "json_schema",
                "status",
            ],
        )

    def _parse_objecttype_data(
        self, objecttypes: list[dict[str, object]]
    ) -> list[ObjectType]:
        data = []
        for objecttype in objecttypes:
            # This attribute was added in 3.4.0 but removed in 3.4.1
            objecttype.pop("linkableToZaken", None)
            objecttype.pop("versions")
            objecttype.pop("url")
            objecttype["is_imported"] = True
            data.append(ObjectType(**_underscoreize_keys(objecttype)))
        return data

    def _parse_objecttypeversion_data(
        self, objecttype_versions: list[dict[str, object]], objecttype
    ) -> list[ObjectTypeVersion]:
        data = []
        for objecttype_version in objecttype_versions:
            objecttype_version.pop("url")
            objecttype_version["objectType"] = objecttype
            data.append(ObjectTypeVersion(**_underscoreize_keys(objecttype_version)))
        return data
