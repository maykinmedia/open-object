from datetime import date

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.constants import DataClassificationChoices, UpdateFrequencyChoices
from objects.core.models import ObjectType
from objects.core.tests.factories import (
    ObjectFactory,
    ObjectTypeFactory,
    ObjectTypeVersionFactory,
)
from objects.utils.test import TokenAuthMixin

from .utils import reverse


@freeze_time("2020-01-01")
class ObjectTypeAPITests(TokenAuthMixin, APITestCase):
    def test_get_objecttypes(self):
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(object_type=object_type)
        url = reverse("objecttype-detail", args=[object_type.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{url}",
                "uuid": str(object_type.uuid),
                "name": object_type.name,
                "namePlural": object_type.name_plural,
                "description": object_type.description,
                "dataClassification": object_type.data_classification,
                "maintainerOrganization": object_type.maintainer_organization,
                "maintainerDepartment": object_type.maintainer_department,
                "contactPerson": object_type.contact_person,
                "contactEmail": object_type.contact_email,
                "source": object_type.source,
                "updateFrequency": object_type.update_frequency,
                "providerOrganization": object_type.provider_organization,
                "documentationUrl": object_type.documentation_url,
                "labels": object_type.labels,
                "createdAt": "2020-01-01",
                "modifiedAt": "2020-01-01",
                "allowGeometry": object_type.allow_geometry,
                "versions": [
                    "http://testserver{url}".format(
                        url=reverse(
                            "objecttypeversion-detail",
                            args=[object_type.uuid, object_version.version],
                        )
                    ),
                ],
            },
        )

    def test_get_objecttypes_with_versions(self):
        object_types = ObjectTypeFactory.create_batch(2)
        object_versions = [
            ObjectTypeVersionFactory.create(object_type=object_type)
            for object_type in object_types
        ]
        for i, object_type in enumerate(object_types):
            with self.subTest(object_type=object_type):
                url = reverse("objecttype-detail", args=[object_type.uuid])

                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                data = response.json()
                self.assertEqual(len(data["versions"]), 1)
                self.assertEqual(
                    data["versions"],
                    [
                        "http://testserver{url}".format(
                            url=reverse(
                                "objecttypeversion-detail",
                                args=[object_type.uuid, object_versions[i].version],
                            )
                        ),
                    ],
                )

    def test_create_objecttype(self):
        url = reverse("objecttype-list")
        data = {
            "name": "boom",
            "namePlural": "bomen",
            "description": "tree type description",
            "dataClassification": DataClassificationChoices.intern,
            "maintainerOrganization": "tree municipality",
            "maintainerDepartment": "object types department",
            "contactPerson": "John Smith",
            "contactEmail": "John.Smith@objecttypes.nl",
            "source": "tree system",
            "updateFrequency": UpdateFrequencyChoices.monthly,
            "providerOrganization": "tree provider",
            "documentationUrl": "http://example.com/doc/trees",
            "labels": {"key1": "value1"},
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ObjectType.objects.count(), 1)

        object_type = ObjectType.objects.get()

        self.assertEqual(object_type.name, "boom")
        self.assertEqual(object_type.name_plural, "bomen")
        self.assertEqual(object_type.description, "tree type description")
        self.assertEqual(
            object_type.data_classification, DataClassificationChoices.intern
        )
        self.assertEqual(object_type.maintainer_organization, "tree municipality")
        self.assertEqual(object_type.maintainer_department, "object types department")
        self.assertEqual(object_type.contact_person, "John Smith")
        self.assertEqual(object_type.contact_email, "John.Smith@objecttypes.nl")
        self.assertEqual(object_type.source, "tree system")
        self.assertEqual(object_type.update_frequency, UpdateFrequencyChoices.monthly)
        self.assertEqual(object_type.provider_organization, "tree provider")
        self.assertEqual(object_type.documentation_url, "http://example.com/doc/trees")
        self.assertEqual(object_type.labels, {"key1": "value1"})
        self.assertEqual(object_type.created_at, date(2020, 1, 1))
        self.assertEqual(object_type.modified_at, date(2020, 1, 1))

    def test_create_objecttype_with_duplicate_uuid(self):
        object_type = ObjectTypeFactory.create()

        url = reverse("objecttype-list")
        data = {
            "uuid": object_type.uuid,
            "name": "boom",
            "namePlural": "bomen",
            "description": "tree type description",
            "dataClassification": DataClassificationChoices.intern,
            "maintainerOrganization": "tree municipality",
            "maintainerDepartment": "object types department",
            "contactPerson": "John Smith",
            "contactEmail": "John.Smith@objecttypes.nl",
            "source": "tree system",
            "updateFrequency": UpdateFrequencyChoices.monthly,
            "providerOrganization": "tree provider",
            "documentationUrl": "http://example.com/doc/trees",
            "labels": {"key1": "value1"},
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_objecttype(self):
        object_type = ObjectTypeFactory.create(
            data_classification=DataClassificationChoices.intern
        )
        url = reverse("objecttype-detail", args=[object_type.uuid])

        response = self.client.patch(
            url,
            {
                "dataClassification": DataClassificationChoices.open,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_type.refresh_from_db()

        self.assertEqual(
            object_type.data_classification, DataClassificationChoices.open
        )

    def test_delete_objecttype(self):
        object_type = ObjectTypeFactory.create()
        url = reverse("objecttype-detail", args=[object_type.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ObjectType.objects.count(), 0)

    def test_delete_objecttype_protected(self):
        obj = ObjectFactory.create()
        object_type = obj.object_type
        url = reverse("objecttype-detail", args=[object_type.uuid])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["title"], "Resource is protected.")
