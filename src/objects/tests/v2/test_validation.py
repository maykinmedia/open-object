import uuid

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import get_validation_errors

from objects.core.models import Object
from objects.core.tests.factories import (
    ObjectRecordFactory,
    ObjectTypeFactory,
    ObjectTypeVersionFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import ClearCachesMixin, TokenAuthMixin

from ...core.constants import ObjectTypeVersionStatus
from ..constants import GEO_WRITE_KWARGS
from .utils import reverse


class ObjectTypeValidationTests(TokenAuthMixin, ClearCachesMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

        self.object_type = ObjectTypeFactory.create()

        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=self.token_auth,
        )

    def test_create_object_with_invalid_length(self):
        data = {
            "type": f"https://testserver/{'a' * 1000}/{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
            },
        }
        url = reverse("object-list")

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()

        self.assertEqual(data["status"], 400)
        self.assertEqual(Object.objects.count(), 0)

        type_error = get_validation_errors(response, "type")

        self.assertEqual(type_error["code"], "max_length")
        self.assertEqual(
            type_error["reason"],
            "The value has too many characters",
        )

    def test_create_object_no_version(self):
        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 10,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            f"Object type {self.object_type} version: 10 does not appear to exist.",
        )

    def test_create_object_schema_invalid(self):
        ObjectTypeVersionFactory.create(object_type=self.object_type)

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "'diameter' is a required property",
        )

    def test_create_object_without_record_invalid(self):
        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_correction_invalid(self):
        ObjectTypeVersionFactory.create(object_type=self.object_type)

        record = ObjectRecordFactory.create()
        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "correctionFor": record.index,
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.exclude(id=record.object.id).count(), 0)

        error = get_validation_errors(response, "record.correctionFor")

        self.assertEqual(
            error["reason"],
            f"Object with index={record.index} does not exist.",
        )

    def test_create_object_geometry_not_allowed(self):
        self.object_type.allow_geometry = False
        self.object_type.save()

        ObjectTypeVersionFactory.create(object_type=self.object_type)

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "This object type doesn't support geometry",
        )

    def test_create_object_with_empty_data_valid(self):
        """
        regression test for https://github.com/maykinmedia/open-object/issues/371
        """
        version = ObjectTypeVersionFactory.create(object_type=self.object_type)
        version.json_schema["required"] = []
        version.save()

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_object_with_empty_data_invalid(
        self,
    ):
        """
        regression test for https://github.com/maykinmedia/open-object/issues/371
        """
        ObjectTypeVersionFactory.create(object_type=self.object_type)

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_object_with_correction_invalid(self):
        ObjectTypeVersionFactory.create(object_type=self.object_type)

        corrected_record, initial_record = ObjectRecordFactory.create_batch(
            2, object__object_type=self.object_type
        )
        object = initial_record.object
        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "correctionFor": 5,
            },
        }

        response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "record.correctionFor")

        self.assertEqual(
            error["reason"],
            "Object with index=5 does not exist.",
        )

    def test_update_object_type_invalid(self):
        old_object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=old_object_type,
            mode=PermissionModes.read_and_write,
            token_auth=self.token_auth,
        )

        initial_record = ObjectRecordFactory.create(
            object__object_type=old_object_type,
            data={"plantDate": "2020-04-12", "diameter": 30},
            version=1,
        )
        obj = initial_record.object

        url = reverse("object-detail", args=[obj.uuid])
        data = {"type": reverse("objecttype-detail", args=[self.object_type.uuid])}

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        type_error = get_validation_errors(response, "type")

        self.assertEqual(type_error["reason"], "This field can't be changed")

    def test_update_uuid_invalid(self):
        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {"uuid": uuid.uuid4()}

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "uuid")

        self.assertEqual(
            error["reason"],
            "This field can't be changed",
        )

    def test_update_geometry_not_allowed(self):
        self.object_type.allow_geometry = False
        self.object_type.save()
        ObjectTypeVersionFactory.create(object_type=self.object_type)

        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type, geometry=None, data={"diameter": 20}
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            }
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "This object type doesn't support geometry",
        )

    def test_create_object_with_duplicate_uuid_returns_400(self):
        ObjectTypeVersionFactory.create(object_type=self.object_type)
        url = reverse("object-list")

        data = {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "uuid")

        self.assertEqual(error["reason"], "An object with this UUID already exists.")
        self.assertEqual(error["code"], "unique")

    def test_patch_objecttype_with_uuid_fail(self):
        object_type = ObjectTypeFactory.create()
        url = reverse("objecttype-detail", args=[object_type.uuid])

        response = self.client.patch(url, {"uuid": uuid.uuid4()})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "uuid")

        self.assertEqual(error["reason"], "This field can't be changed")
        self.assertEqual(error["code"], "immutable-field")

    def test_delete_objecttype_with_versions_fail(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(object_type=object_type)
        url = reverse("objecttype-detail", args=[object_type.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "All related versions should be destroyed before destroying the objecttype",
        )
        self.assertEqual(error["code"], "pending-versions")


class ObjectTypeVersionValidationTests(TokenAuthMixin, APITestCase):
    def test_create_version_with_incorrect_schema_fail(self):
        object_type = ObjectTypeFactory.create()
        url = reverse("objecttypeversion-list", args=[object_type.uuid])
        data = {
            "jsonSchema": {
                "title": "Tree",
                "$schema": "https://json-schema.org/draft/2020-12/schema#",
                "type": "any",
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "jsonSchema")

        self.assertEqual(error["code"], "invalid-json-schema")
        self.assertEqual(
            error["reason"], "'any' is not valid under any of the given schemas"
        )

    def test_create_version_with_incorrect_objecttype_fail(self):
        url = reverse("objecttypeversion-list", args=[uuid.uuid4()])
        data = {
            "jsonSchema": {
                "title": "Tree",
                "$schema": "https://json-schema.org/draft/2020-12/schema#",
                "properties": {
                    "diameter": {"type": "integer", "description": "size in cm."}
                },
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(error["code"], "invalid-objecttype")
        self.assertEqual(error["reason"], "Objecttype url is invalid")

    def test_update_published_version_fail(self):
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.published
        )
        url = reverse(
            "objecttypeversion-detail",
            args=[object_type.uuid, object_version.version],
        )
        new_json_schema = {
            "type": "object",
            "title": "Tree",
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "required": ["diameter"],
            "properties": {"diameter": {"type": "number"}},
        }

        response = self.client.put(url, {"jsonSchema": new_json_schema})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(error["code"], "non-draft-version-update")
        self.assertEqual(error["reason"], "Only draft versions can be changed")

    def test_delete_puclished_version_fail(self):
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.published
        )
        url = reverse(
            "objecttypeversion-detail",
            args=[object_type.uuid, object_version.version],
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(error["code"], "non-draft-version-destroy")
        self.assertEqual(error["reason"], "Only draft versions can be destroyed")
