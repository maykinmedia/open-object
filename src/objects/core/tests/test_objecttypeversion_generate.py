from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from objects.core.models import ObjectTypeVersion
from objects.core.tests.factories import ObjectTypeFactory, ObjectTypeVersionFactory
from objects.core.utils import check_objecttype

JSON_SCHEMA = {
    "type": "object",
    "title": "Tree",
    "$schema": "https://json-schema.org/draft/2020-12/schema#",
    "required": ["diameter"],
    "properties": {
        "diameter": {"type": "integer", "description": "size in cm."},
        "email": {"type": "string", "format": "email"},
        "start_time": {"type": "string", "format": "time"},
    },
}


class GenerateVersionTests(TestCase):
    def test_generate_version_for_new_objecttype(self):
        object_type = ObjectTypeFactory.create()

        object_version = ObjectTypeVersion.objects.create(
            json_schema=JSON_SCHEMA, object_type=object_type
        )

        self.assertEqual(object_version.version, 1)

    def test_generate_version_for_objecttype_with_existed_version(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(object_type=object_type, version=1)

        object_version = ObjectTypeVersion.objects.create(
            json_schema=JSON_SCHEMA, object_type=object_type
        )

        self.assertEqual(object_version.version, 2)

    def test_version_bounds_check(self):
        object_type = ObjectTypeFactory.create()
        max_sql_smallint = (1 << 15) - 1
        ObjectTypeVersionFactory.create(
            object_type=object_type, version=max_sql_smallint
        )

        with self.assertRaises(ValidationError):
            ObjectTypeVersion.objects.create(
                json_schema=JSON_SCHEMA, object_type=object_type
            )


class ObjectTypeVersionJsonSchemaValidationTestCase(TestCase):
    def test_strict_format_checker_defaults_from_settings(self):
        with override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=False):
            version = ObjectTypeVersionFactory.create()
            self.assertFalse(version.strict_format_checker)

            version.strict_format_checker = True
            version.save()
            self.assertTrue(version.strict_format_checker)

        with override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=False):
            version = ObjectTypeVersionFactory.create(strict_format_checker=True)
            self.assertTrue(version.strict_format_checker)

        with override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=True):
            version = ObjectTypeVersionFactory.create()
            self.assertTrue(version.strict_format_checker)

            version.strict_format_checker = False
            version.save()
            self.assertFalse(version.strict_format_checker)

    def test_invalid_email(self):
        object_type = ObjectTypeFactory.create()
        version = ObjectTypeVersionFactory.create(
            object_type=object_type,
            json_schema=JSON_SCHEMA,
            strict_format_checker=False,
        )
        check_objecttype(
            object_type,
            version.version,
            {"email": "not-an-email", "diameter": 10},
        )

        with self.assertRaises(ValidationError):
            version.strict_format_checker = True
            version.save()
            check_objecttype(
                object_type,
                version.version,
                {"email": "not-an-email", "diameter": 10},
            )

    def test_valid_email(self):
        object_type = ObjectTypeFactory.create()
        version = ObjectTypeVersionFactory.create(
            object_type=object_type,
            json_schema=JSON_SCHEMA,
            strict_format_checker=True,
        )
        check_objecttype(
            object_type,
            version.version,
            {"email": "valid@example.com", "diameter": 10},
        )

        version.strict_format_checker = False
        version.save()
        check_objecttype(
            object_type,
            version.version,
            {"email": "valid@example.com", "diameter": 10},
        )

    def test_invalid_time(self):
        object_type = ObjectTypeFactory.create()
        version = ObjectTypeVersionFactory.create(
            object_type=object_type,
            json_schema=JSON_SCHEMA,
            strict_format_checker=False,
        )
        check_objecttype(
            object_type,
            version.version,
            {"start_time": "not-a-time", "diameter": 10},
        )

        with self.assertRaises(ValidationError):
            version.strict_format_checker = True
            version.save()
            check_objecttype(
                object_type,
                version.version,
                {"start_time": "not-a-time", "diameter": 10},
            )

    def test_valid_time(self):
        object_type = ObjectTypeFactory.create()
        version = ObjectTypeVersionFactory.create(
            object_type=object_type,
            json_schema=JSON_SCHEMA,
            strict_format_checker=True,
        )
        check_objecttype(
            object_type,
            version.version,
            {"start_time": "12:34:56Z", "diameter": 10},
        )

        version.strict_format_checker = False
        version.save()
        check_objecttype(
            object_type,
            version.version,
            {"start_time": "12:34:56Z", "diameter": 10},
        )
