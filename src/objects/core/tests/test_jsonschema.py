from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase

from jsonschema import FormatError
from jsonschema._format import _draft_checkers

from ..utils import (
    is_valid_color,
    is_valid_email,
    validate_jsonschema,
)

SCHEMA_ALL_FORMATS = {
    "type": "object",
    "properties": {
        "color": {"type": "string", "format": "color"},
        "date": {"type": "string", "format": "date"},
        "date-time": {"type": "string", "format": "date-time"},
        "duration": {"type": "string", "format": "duration"},
        "email": {"type": "string", "format": "email"},
        "hostname": {"type": "string", "format": "hostname"},
        "idn-hostname": {"type": "string", "format": "idn-hostname"},
        "ipv4": {"type": "string", "format": "ipv4"},
        "ipv6": {"type": "string", "format": "ipv6"},
        "iri": {"type": "string", "format": "iri"},
        "iri-reference": {"type": "string", "format": "iri-reference"},
        "json-pointer": {"type": "string", "format": "json-pointer"},
        "regex": {"type": "string", "format": "regex"},
        "relative-json-pointer": {"type": "string", "format": "relative-json-pointer"},
        "time": {"type": "string", "format": "time"},
        "uri": {"type": "string", "format": "uri"},
        "uri-reference": {"type": "string", "format": "uri-reference"},
        "uri-template": {"type": "string", "format": "uri-template"},
        "uuid": {"type": "string", "format": "uuid"},
    },
}


class TestValidateJsonSchema(TestCase):
    def setUp(self):
        self.schema = {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "name": {"type": "string"},
            },
            "required": ["price", "name"],
        }

    def test_valid_data_passes(self):
        validate_jsonschema({"price": 10, "name": "test"}, self.schema)

    def test_missing_required_field_raises(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'price' is a required property"
        ):
            validate_jsonschema({"name": "Eggs"}, self.schema)

    def test_missing_all_required_fields_raises(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'price' is a required property"
        ):
            validate_jsonschema({}, self.schema)

    def test_wrong_type_raises(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'not-a-number' is not of type 'number'"
        ):
            validate_jsonschema({"price": "not-a-number", "name": "Eggs"}, self.schema)

    def test_format_checker_disabled_ignores_invalid_format(self):
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
            "required": ["email"],
        }
        # format not enforced
        validate_jsonschema(
            {"email": "not-an-email"}, self.schema, use_format_checker=False
        )

    def test_format_checker_enabled_rejects_invalid_format(self):
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
            "required": ["email"],
        }
        with self.assertRaises(DjangoValidationError):
            validate_jsonschema(
                {"email": "not-an-email"}, self.schema, use_format_checker=True
            )

    def test_format_checker_enabled_accepts_valid_format(self):
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
            "required": ["email"],
        }
        validate_jsonschema(
            {"email": "valid@example.com"}, self.schema, use_format_checker=True
        )

    def test_valid_email_passes_on_all_drafts(self):
        for draft_name, checker in _draft_checkers.items():
            with self.subTest(draft=draft_name):
                self.assertIn("email", checker.checkers)
                self.assertTrue(checker.check("valid@example.com", "email") is None)

    def test_invalid_email_passes_when_checker_is_removed(self):
        for draft_name, checker in _draft_checkers.items():
            with self.subTest(draft=draft_name):
                original = checker.checkers.pop("email")
                try:
                    checker.check("not-an-email", "email")
                finally:
                    # restore so other for other tests
                    checker.checkers["email"] = original


class JSONSchemaFormatTests(TestCase):
    def test_color(self):
        data = {}
        invalid_values = ["#12", "#12345", "#zzzzzz", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["color"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"color": "#ff0000"}, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"color": "red"}, SCHEMA_ALL_FORMATS)

    def test_date(self):
        data = {}
        invalid_values = ["2026-13-40", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["date"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date": "2026-01-01"}, SCHEMA_ALL_FORMATS)

    def test_date_time(self):
        data = {}
        invalid_values = ["2026-13-40T25:61:61Z", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["date-time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date-time": "2026-01-01T12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_duration(self):
        data = {}
        invalid_values = ["not-a-duration", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["duration"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"duration": "P3Y6M4DT12H30M5S"}, SCHEMA_ALL_FORMATS)

    def test_email(self):
        data = {}
        invalid_values = ["test", None, "123", 123, "test-test@.test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["email"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"email": "test@example.com"}, SCHEMA_ALL_FORMATS)

    def test_hostname(self):
        data = {}
        invalid_values = ["-invalid-host", "invalid_host", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"hostname": "example.com"}, SCHEMA_ALL_FORMATS)

    def test_idn_hostname(self):
        data = {}
        invalid_values = ["-invalid.com", "invalid-.com", "inv@lid.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["idn-hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["münchen.com", "tęst.com", "crème.fr"]
        for val in valid_values:
            data["idn-hostname"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_ipv4(self):
        data = {}
        invalid_values = ["999.999.999.999", "abc.def.ghi.jkl", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["ipv4"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"ipv4": "192.168.1.1"}, SCHEMA_ALL_FORMATS)

    def test_ipv6(self):
        data = {}
        invalid_values = ["invalid:ipv6", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["ipv6"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}, SCHEMA_ALL_FORMATS
        )

    def test_iri(self):
        data = {}
        invalid_values = ["http://exa mple.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["iri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["https://example.com", "https://münchen.com/über"]
        for val in valid_values:
            data["iri"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_iri_reference(self):
        data = {}
        invalid_refs = ["ht tp://example.com", "://missing.scheme.com", None, 123]
        for val in invalid_refs:
            with self.assertRaises(DjangoValidationError):
                data["iri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_refs = ["/relative/path", "crème/cheese", "münchen/über"]
        for val in valid_refs:
            data["iri-reference"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_json_pointer(self):
        data = {}
        invalid_values = ["foo/bar", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"json-pointer": "/foo/bar"}, SCHEMA_ALL_FORMATS)

    def test_regex(self):
        data = {}
        invalid_values = ["[unclosed", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["regex"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"regex": "^[a-z]+$"}, SCHEMA_ALL_FORMATS)

    def test_relative_json_pointer(self):
        data = {}
        invalid_values = ["foo", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["relative-json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"relative-json-pointer": "0/foo"}, SCHEMA_ALL_FORMATS)

    def test_time(self):
        data = {}
        invalid_values = ["25:61:61", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"time": "12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_uri(self):
        data = {}
        invalid_values = ["not-a-uri", "://missing", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri": "https://example.com/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_reference(self):
        data = {}
        invalid_values = [None, 123, "http://[invalid"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-reference": "/relative/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_template(self):
        data = {}
        invalid_values = [None, 123, "{unclosed"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri-template"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-template": "/users/{id}"}, SCHEMA_ALL_FORMATS)

    def test_uuid(self):
        data = {}
        invalid_values = ["not-a-uuid", None, 123, "1234"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uuid"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"uuid": "123e4567-e89b-12d3-a456-426614174000"}, SCHEMA_ALL_FORMATS
        )


class JsonSchemaFormatValidatorsTestCase(TestCase):
    def test_email(self):
        invalid_emails = [
            "test",
            "@missingusername.com",
            "username@.com",
            "user@site..com",
            "user@com",
            "user@site,com",
            None,
            123,
        ]
        for email in invalid_emails:
            self.assertFalse(is_valid_email(email))

        valid_emails = [
            "user@example.com",
            "user.name+tag@example.co.uk",
            "user_name-test@example.com",
            "user!?name@example.io",
            "user123@example123.com",
        ]
        for email in valid_emails:
            self.assertTrue(is_valid_email(email))

    def test_color(self):
        invalid_colors = ["notacolor", "123456", "#12345G"]
        for color in invalid_colors:
            with self.assertRaises(FormatError):
                is_valid_color(color)

        valid_colors = ["red", "#fff", "#FFFFFF"]
        for color in valid_colors:
            self.assertTrue(is_valid_color(color))
