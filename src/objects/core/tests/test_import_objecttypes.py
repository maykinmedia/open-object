from django.core.management import CommandError, call_command

import hypothesis.strategies as st
import requests_mock
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis.extra.django import TestCase
from zgw_consumers.models import Service

from objects.core.models import ObjectType, ObjectTypeVersion

from .strategies import objecttypes


def _to_api_objecttype(ot: ObjectType, base_url: str) -> dict:
    """Serialize an ObjectType to API response format."""
    assert ot.created_at and ot.modified_at
    version_urls = [
        f"{base_url}objecttypes/{ot.uuid}/versions/{v.version}"
        for v in ot.versions.order_by("version")
    ]
    return {
        "url": f"{base_url}objecttypes/{ot.uuid}",
        "uuid": str(ot.uuid),
        "name": ot.name,
        "namePlural": ot.name_plural,
        "description": ot.description,
        "dataClassification": ot.data_classification,
        "maintainerOrganization": ot.maintainer_organization,
        "maintainerDepartment": ot.maintainer_department,
        "contactPerson": ot.contact_person,
        "contactEmail": ot.contact_email,
        "source": ot.source,
        "updateFrequency": ot.update_frequency,
        "providerOrganization": ot.provider_organization,
        "documentationUrl": ot.documentation_url,
        "labels": ot.labels,
        "allowGeometry": ot.allow_geometry,
        "createdAt": str(ot.created_at),
        "modifiedAt": str(ot.modified_at),
        "versions": version_urls,
    }


def _to_api_versions(ot: ObjectType, base_url: str) -> dict:
    """Serialize ObjectType versions to API response format."""
    versions = ot.versions.order_by("version")
    results = [
        {
            "url": f"{base_url}objecttypes/{ot.uuid}/versions/{v.version}",
            "version": v.version,
            "objectType": f"{base_url}objecttypes/{ot.uuid}",
            "status": v.status,
            "jsonSchema": v.json_schema,
            "createdAt": str(v.created_at),
            "modifiedAt": str(v.modified_at),
            **({"publishedAt": str(v.published_at)} if v.published_at else {}),
        }
        for v in versions
    ]
    return {
        "count": len(results),
        "next": None,
        "previous": None,
        "results": results,
    }


class TestImportObjectTypesCommand(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "http://127.0.0.1:8000/api/v2/"
        cls.service = Service.objects.create(api_root=cls.url, slug="objecttypes-api")
        return super().setUpTestData()

    def setUp(self):
        super().setUp()

        self.m = requests_mock.Mocker()
        self.m.start()

        self.m.head(self.url, status_code=200, headers={"api-version": "2.2.2"})

    def tearDown(self):
        self.m.stop()

    def setup_example(self):
        # create a fresh Mocker, m.reset() does *not* remove existing matchers
        self.m.stop()
        self.m = requests_mock.Mocker()
        self.m.start()
        self.m.head(self.url, status_code=200, headers={"api-version": "2.2.2"})
        return super().setup_example()

    def teardown_example(self, example):
        self.m.stop()
        self.m = requests_mock.Mocker()
        self.m.start()
        return super().teardown_example(example)

    def _call_command(self):
        call_command("import_objecttypes", self.service.slug)

    def test_api_version_is_required(self):
        self.m.head(self.url, status_code=200)

        with self.assertRaisesMessage(
            CommandError, "API version must be 2.2.2 or higher"
        ):
            self._call_command()

    def test_api_version_must_be_greater_than_constant(self):
        self.m.head(self.url, status_code=200, headers={"api-version": "2.1.0"})

        with self.assertRaisesMessage(
            CommandError, "API version must be 2.2.2 or higher"
        ):
            self._call_command()

    def test_command_fails_if_http_error(self):
        self.m.get(f"{self.url}objecttypes", status_code=404)
        with self.assertRaises(CommandError):
            self._call_command()

    def test_command_fails_on_missing_service(self):
        with self.assertRaisesMessage(CommandError, "Service 'SRV-man' does not exist"):
            call_command("import_objecttypes", "SRV-man")

    @given(
        objecttypes=st.lists(
            objecttypes(min_versions=1, max_versions=3), min_size=1, max_size=3
        )
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        phases=set(Phase) - {Phase.shrink},
    )
    def test_new_objecttypes_are_created(self, objecttypes: list[ObjectType]) -> None:
        api_results = [_to_api_objecttype(ot, self.url) for ot in objecttypes]
        ot_response = {
            "count": len(objecttypes),
            "next": None,
            "previous": None,
            "results": api_results,
        }

        self.m.get(f"{self.url}objecttypes", json=ot_response)
        for ot in objecttypes:
            self.m.get(
                f"{self.url}objecttypes/{ot.uuid}/versions",
                json=_to_api_versions(ot, self.url),
            )

        original_data = {
            ot.uuid: {
                "ot": ot,
                "versions": list(ot.versions.order_by("version")),
            }
            for ot in objecttypes
        }

        ObjectType.objects.all().delete()
        ObjectTypeVersion.objects.all().delete()

        self._call_command()

        assert ObjectType.objects.count() == len(objecttypes)

        for ot_uuid, original in original_data.items():
            original_ot = original["ot"]
            db_ot = ObjectType.objects.get(uuid=ot_uuid)

            assert db_ot.is_imported is True
            assert db_ot.name == original_ot.name
            assert db_ot.name_plural == original_ot.name_plural
            assert db_ot.description == original_ot.description
            assert db_ot.data_classification == original_ot.data_classification
            assert db_ot.maintainer_organization == original_ot.maintainer_organization
            assert db_ot.maintainer_department == original_ot.maintainer_department
            assert db_ot.contact_person == original_ot.contact_person
            assert db_ot.contact_email == original_ot.contact_email
            assert db_ot.source == original_ot.source
            assert db_ot.update_frequency == original_ot.update_frequency
            assert db_ot.provider_organization == original_ot.provider_organization
            assert db_ot.documentation_url == original_ot.documentation_url
            assert db_ot.labels == original_ot.labels
            assert db_ot.allow_geometry == original_ot.allow_geometry

            original_versions = original["versions"]
            assert db_ot.versions.count() == len(original_versions)

            for orig_ver in original_versions:
                db_version = ObjectTypeVersion.objects.get(
                    object_type=db_ot, version=orig_ver.version
                )
                assert db_version.json_schema == orig_ver.json_schema
                assert db_version.status == orig_ver.status

    @given(
        objecttypes=st.lists(
            objecttypes(min_versions=2, max_versions=3), min_size=1, max_size=3
        )
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        phases=set(Phase) - {Phase.shrink},
    )
    def test_existing_objecttypes_are_updated(
        self, objecttypes: list[ObjectType]
    ) -> None:
        api_results = [_to_api_objecttype(ot, self.url) for ot in objecttypes]
        ot_response = {
            "count": len(objecttypes),
            "next": None,
            "previous": None,
            "results": api_results,
        }

        self.m.get(f"{self.url}objecttypes", json=ot_response)
        for ot in objecttypes:
            self.m.get(
                f"{self.url}objecttypes/{ot.uuid}/versions",
                json=_to_api_versions(ot, self.url),
            )

        original_data = {
            ot.uuid: {
                "ot": ot,
                "versions": list(ot.versions.order_by("version")),
            }
            for ot in objecttypes
        }

        # Modify the db, so we can see an update done by the import
        ObjectType.objects.update(name="Old Name")
        last_version = objecttypes[0].versions.last()
        assert last_version
        last_version.delete()

        self._call_command()

        assert ObjectType.objects.count() == len(objecttypes)

        for ot_uuid, original in original_data.items():
            api_ot = original["ot"]
            db_ot = ObjectType.objects.get(uuid=ot_uuid)

            # Verify fields were updated from old values to API values
            assert db_ot.is_imported is True
            assert db_ot.name == api_ot.name
            assert db_ot.name != "Old Name"
            assert db_ot.name_plural == api_ot.name_plural
            assert db_ot.description == api_ot.description
            assert db_ot.data_classification == api_ot.data_classification
            assert db_ot.maintainer_organization == api_ot.maintainer_organization
            assert db_ot.maintainer_department == api_ot.maintainer_department
            assert db_ot.contact_person == api_ot.contact_person
            assert db_ot.contact_email == api_ot.contact_email
            assert db_ot.source == api_ot.source
            assert db_ot.update_frequency == api_ot.update_frequency
            assert db_ot.provider_organization == api_ot.provider_organization
            assert db_ot.documentation_url == api_ot.documentation_url
            assert db_ot.labels == api_ot.labels
            assert db_ot.allow_geometry == api_ot.allow_geometry

            api_versions = original["versions"]
            assert db_ot.versions.count() == len(api_versions)

            for api_ver in api_versions:
                db_version = ObjectTypeVersion.objects.get(
                    object_type=db_ot, version=api_ver.version
                )
                assert db_version.json_schema == api_ver.json_schema
                assert db_version.status == api_ver.status
