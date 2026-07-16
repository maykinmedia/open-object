import json
import zipfile
from datetime import date
from io import BytesIO

from django.urls import reverse, reverse_lazy

import requests_mock
from django_webtest import WebTest
from freezegun import freeze_time
from maykin_2fa.test import disable_admin_mfa
from webtest import Upload

from objects.accounts.tests.factories import SuperUserFactory
from objects.core.constants import (
    DataClassificationChoices,
    ObjectTypeVersionStatus,
    UpdateFrequencyChoices,
)
from objects.core.import_export import export_data
from objects.core.models import ObjectType
from objects.core.tests.factories import ObjectTypeFactory, ObjectTypeVersionFactory

JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema#",
    "type": "object",
    "title": "Tree",
    "description": (
        "A woody plant (deciduous or coniferous) with a root system and a "
        "single, sturdy, woody stem, branching above the ground."
    ),
    "required": ["diameter"],
    "properties": {"diameter": {"type": "integer", "description": "size in cm."}},
}


@freeze_time("2020-01-01")
@disable_admin_mfa()
class AdminAddTests(WebTest):
    url = reverse_lazy("admin:core_objecttype_add")
    import_from_url = reverse_lazy("admin:import_from_url")
    import_from_file = reverse_lazy("admin:import_from_file")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = SuperUserFactory.create()

    def setUp(self) -> None:
        super().setUp()

        self.app.set_user(self.user)

    def test_create_objecttype_success(self):
        get_response = self.app.get(self.url)

        form = get_response.forms[1]
        form["name"] = "boom"
        form["name_plural"] = "bomen"
        form["description"] = "some object type description"
        form["data_classification"] = DataClassificationChoices.intern
        form["maintainer_organization"] = "tree municipality"
        form["maintainer_department"] = "object types department"
        form["contact_person"] = "John Smith"
        form["contact_email"] = "John.Smith@objecttypes.nl"
        form["source"] = "tree system"
        form["update_frequency"] = UpdateFrequencyChoices.monthly
        form["provider_organization"] = "tree provider"
        form["documentation_url"] = "http://example.com/doc/trees"
        form["labels"] = json.dumps({"key1": "value1"})
        form["versions-0-json_schema"] = json.dumps(JSON_SCHEMA)

        response = form.submit()

        # redirect on successful create, 200 on validation errors, 500 on db errors
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ObjectType.objects.count(), 1)

        object_type = ObjectType.objects.get()

        self.assertEqual(object_type.name, "boom")
        self.assertEqual(object_type.name_plural, "bomen")
        self.assertEqual(object_type.description, "some object type description")
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
        self.assertEqual(object_type.versions.count(), 1)

        object_version = object_type.last_version

        self.assertEqual(object_version.version, 1)
        self.assertEqual(object_version.json_schema, JSON_SCHEMA)
        self.assertEqual(object_version.status, ObjectTypeVersionStatus.draft)
        self.assertEqual(object_version.created_at, date(2020, 1, 1))
        self.assertEqual(object_version.modified_at, date(2020, 1, 1))
        self.assertIsNone(object_version.published_at)

    def test_create_objecttype_invalid_json_schema(self):
        get_response = self.app.get(self.url)

        form = get_response.forms[1]
        form["name"] = "boom"
        form["name_plural"] = "bomen"
        form["description"] = "some object type description"
        form["data_classification"] = DataClassificationChoices.intern
        form["maintainer_organization"] = "tree municipality"
        form["maintainer_department"] = "object types department"
        form["contact_person"] = "John Smith"
        form["contact_email"] = "John.Smith@objecttypes.nl"
        form["source"] = "tree system"
        form["update_frequency"] = UpdateFrequencyChoices.monthly
        form["provider_organization"] = "tree provider"
        form["documentation_url"] = "http://example.com/doc/trees"
        form["labels"] = json.dumps({"key1": "value1"})
        form["versions-0-json_schema"] = "{}{"

        response = form.submit()

        # redirect on successful create, 200 on validation errors, 500 on db errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ObjectType.objects.count(), 0)

        error_list = response.html.find("ul", {"class": "errorlist"})

        # The submitted value is shown in the error
        self.assertIn("{}{", error_list.text)

        json_schema_field = response.forms[1].fields["versions-0-json_schema"][0]

        # Verify that the value of the JSON schema field is the fallback value
        self.assertEqual(json_schema_field.value, "{}")

    def test_create_objecttype_without_version_fail(self):
        get_response = self.app.get(self.url)

        form = get_response.forms[1]
        form["name"] = "boom"
        form["name_plural"] = "bomen"
        form["description"] = "some object type description"
        form["maintainer_organization"] = "tree municipality"

        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ObjectType.objects.count(), 0)

    def test_create_objecttype_with_invalid_json_schema(self):
        get_response = self.app.get(self.url)

        form = get_response.forms[1]
        form["name"] = "boom"
        form["name_plural"] = "bomen"
        form["description"] = "some object type description"
        form["maintainer_organization"] = "tree municipality"
        form["versions-0-json_schema"] = json.dumps(
            {
                "title": "Tree",
                "$schema": "https://json-schema.org/draft/2020-12/schema#",
                "type": "any",
            }
        )

        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ObjectType.objects.count(), 0)

    @requests_mock.Mocker()
    def test_create_objecttype_from_url(self, m):
        get_response = self.app.get(self.import_from_url)

        m.get("https://example.com/tree.json", json=JSON_SCHEMA)

        form = get_response.form
        form["objecttype_url"] = "https://example.com/tree.json"
        form["name_plural"] = "Trees"

        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ObjectType.objects.count(), 1)

        object_type = ObjectType.objects.get()

        self.assertEqual(object_type.name, "Tree")
        self.assertEqual(object_type.name_plural, "Trees")
        self.assertEqual(
            object_type.description,
            "A woody plant (deciduous or coniferous) with a root system and a single, sturdy, woody stem, branching "
            "above the ground.",
        )
        self.assertEqual(
            object_type.data_classification, DataClassificationChoices.open
        )
        self.assertEqual(object_type.created_at, date(2020, 1, 1))
        self.assertEqual(object_type.modified_at, date(2020, 1, 1))
        self.assertEqual(object_type.versions.count(), 1)

        object_version = object_type.last_version

        self.assertEqual(object_version.version, 1)
        self.assertEqual(object_version.status, ObjectTypeVersionStatus.draft)
        self.assertEqual(object_version.created_at, date(2020, 1, 1))
        self.assertEqual(object_version.modified_at, date(2020, 1, 1))
        self.assertIsNone(object_version.published_at)
        self.assertEqual(object_version.json_schema, JSON_SCHEMA)

    @requests_mock.Mocker()
    def test_create_objecttype_from_url_with_invalid_schema(self, m):
        get_response = self.app.get(self.import_from_url)

        m.get(
            "https://example.com/tree.json",
            json={
                "title": "Tree",
                "$schema": "https://json-schema.org/draft/2020-12/schema#",
                "type": "any",
            },
        )

        form = get_response.form
        form["objecttype_url"] = "https://example.com/tree.json"
        form["name_plural"] = "bomen"

        response = form.submit()

        self.assertIn("Invalid JSON schema.", response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ObjectType.objects.count(), 0)

    def test_create_objecttype_from_url_with_nonexistent_url(self):
        get_response = self.app.get(self.import_from_url)

        form = get_response.form
        form["objecttype_url"] = "https://random-url123.com"
        form["name_plural"] = "bomen"

        response = form.submit()

        self.assertIn("The Objecttype URL does not exist.", response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ObjectType.objects.count(), 0)

    def test_create_import_from_file_requires_authentication(self):
        self.app.set_user(None)
        import_view = self.app.get(self.import_from_file, expect_errors=True)
        self.assertEqual(import_view.status_code, 302)
        self.assertIn("/admin/login", import_view.location)

    def test_create_import_from_file(self):
        # setup an export file for import
        objecttype = ObjectTypeFactory.create()
        output = BytesIO()
        export_data(output, objecttypes=[objecttype])
        export_file_content = output.getvalue()

        # submit the import form with the export file
        import_view = self.app.get(self.import_from_file)
        form = import_view.form
        form["export_file"] = Upload(
            "test-export.zip", export_file_content, "application/zip"
        )
        response = form.submit()

        # verify redirection after successful import
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/admin/core/objecttype/")

        # check that the objecttype was imported
        self.assertEqual(ObjectType.objects.count(), 2)

    def test_create_import_from_file_invalid_zip(self):
        objecttype = ObjectTypeFactory.create()
        output = BytesIO()
        export_data(output, objecttypes=[objecttype])
        # corrupt the zip content by truncating it
        export_file_content = output.getvalue()[:10]

        import_view = self.app.get(self.import_from_file)
        form = import_view.form
        form["export_file"] = Upload(
            "test-export.zip", export_file_content, "application/zip"
        )
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is not a supported file type")

    def test_create_import_from_file_empty(self):
        import_view = self.app.get(self.import_from_file)
        form = import_view.form
        # create an empty zip file
        empty_zip = BytesIO()
        with zipfile.ZipFile(empty_zip, "w") as zf:
            zf.writestr("README.md", b"This is the wrong file")
        empty_zip.seek(0)

        form["export_file"] = Upload("empty.zip", empty_zip.read(), "application/zip")
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Found nothing importable in that file")

    def test_create_import_from_file_validation_error(self):
        objecttype = ObjectTypeFactory.create()

        # invalidate some property
        objecttype.update_frequency = 1024 * "x"

        output = BytesIO()
        export_data(output, objecttypes=[objecttype])
        export_file_content = output.getvalue()

        import_view = self.app.get(self.import_from_file)
        form = import_view.form
        form["export_file"] = Upload(
            "corrupted-export.zip", export_file_content, "application/zip"
        )
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Row")
        # this error is there if no other errors were found, but nothing was
        # imported, because some random zip was uploaded
        self.assertNotContains(response, "Found nothing importable in that file")

    def test_create_import_from_file_no_file_selected(self):
        import_view = self.app.get(self.import_from_file)
        form = import_view.form
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_export_action(self):
        objecttype1 = ObjectTypeFactory.create(name="Tree 1")
        objecttype2 = ObjectTypeFactory.create(name="Tree 2")

        response = self.app.get(reverse("admin:core_objecttype_changelist"))
        form = response.forms["changelist-form"]
        form["action"] = "export_objecttypes_action"
        form["_selected_action"] = [objecttype1.pk, objecttype2.pk]
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn(
            'attachment; filename="objecttypes-export.zip"',
            response["Content-Disposition"],
        )

        # verify the exported content
        output = BytesIO(response.content)
        with zipfile.ZipFile(output, "r") as zf:
            self.assertIn("objectTypes.json", zf.namelist())

            with zf.open("objectTypes.json") as f:
                data = json.load(f)
                self.assertEqual({d["name"] for d in data}, {"Tree 1", "Tree 2"})


@disable_admin_mfa()
class AdminDetailTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = SuperUserFactory.create()

    def setUp(self) -> None:
        super().setUp()

        self.app.set_user(self.user)

    def test_display_successfully_without_versions(self):
        object_type = ObjectTypeFactory.create()
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        self.assertEqual(get_response.status_code, 200)

        form = get_response.forms[1]

        self.assertEqual(form["versions-0-id"].value, "")

    def test_display_only_last_version(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create_batch(3, object_type=object_type)
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)
        form = get_response.forms[1]

        self.assertEqual(int(form["versions-TOTAL_FORMS"].value), 1)
        self.assertEqual(int(form["versions-0-id"].value), object_type.last_version.id)

    def test_update_draft(self):
        old_schema = {
            "type": "object",
            "title": "Tree",
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "properties": {
                "diameter": {"type": "integer", "description": "size in cm."}
            },
        }
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(
            object_type=object_type, json_schema=old_schema
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        save_button = get_response.html.find("input", {"name": "_save"})
        self.assertIsNotNone(save_button)

        form = get_response.forms[1]
        form["versions-0-json_schema"] = json.dumps(JSON_SCHEMA)
        response = form.submit()

        self.assertEqual(response.status_code, 302)

        object_version.refresh_from_db()
        self.assertEqual(object_version.json_schema, JSON_SCHEMA)

    def test_update_draft_invalid_json_schema(self):
        old_schema = {
            "type": "object",
            "title": "Tree",
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "properties": {
                "diameter": {"type": "integer", "description": "size in cm."}
            },
        }
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(
            object_type=object_type, json_schema=old_schema
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        save_button = get_response.html.find("input", {"name": "_save"})
        self.assertIsNotNone(save_button)

        form = get_response.forms[1]
        form["versions-0-json_schema"] = "{}{"
        response = form.submit()

        self.assertEqual(response.status_code, 200)

        object_version.refresh_from_db()
        self.assertEqual(object_version.json_schema, old_schema)

        error_list = response.html.find("ul", {"class": "errorlist"})

        # The submitted value is shown in the error
        self.assertIn("{}{", error_list.text)

        json_schema_field = response.forms[1].fields["versions-0-json_schema"][0]

        # Verify that the value of the JSON schema field is the fallback value
        self.assertEqual(json_schema_field.value, json.dumps(old_schema))

    def test_update_draft_save_button(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.draft
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        save_button = get_response.html.find("input", {"name": "_save"})
        self.assertIsNotNone(save_button)

    def test_update_published_save_button(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.published
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        save_button = get_response.html.find("input", {"name": "_save"})
        self.assertIsNotNone(save_button)

    def test_publish_draft(self):
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(object_type=object_type)
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        publish_button = get_response.html.find("input", {"name": "_publish"})
        self.assertIsNotNone(publish_button)

        form = get_response.forms[1]
        response = form.submit("_publish")

        self.assertEqual(response.status_code, 302)

        object_version.refresh_from_db()
        self.assertEqual(object_version.status, ObjectTypeVersionStatus.published)
        self.assertEqual(object_version.published_at, date.today())

    def test_publish_published_no_button(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.published
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        publish_button = get_response.html.find("input", {"name": "_publish"})
        self.assertIsNone(publish_button)

    def test_new_version_draft_no_button(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(object_type=object_type)
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        new_version_button = get_response.html.find("input", {"name": "_newversion"})
        self.assertIsNone(new_version_button)

    @freeze_time("2020-02-02")
    def test_new_version_published(self):
        object_type = ObjectTypeFactory.create()
        object_version = ObjectTypeVersionFactory.create(
            object_type=object_type, status=ObjectTypeVersionStatus.published
        )
        url = reverse("admin:core_objecttype_change", args=[object_type.id])

        get_response = self.app.get(url)

        new_version_button = get_response.html.find("input", {"name": "_newversion"})
        self.assertIsNotNone(new_version_button)

        form = get_response.forms[1]
        response = form.submit("_newversion")

        self.assertEqual(response.status_code, 302)

        object_type.refresh_from_db()
        self.assertEqual(object_type.versions.count(), 2)

        last_version = object_type.last_version
        self.assertNotEqual(last_version, object_version)
        self.assertEqual(last_version.version, object_version.version + 1)
        self.assertEqual(last_version.json_schema, object_version.json_schema)
        self.assertEqual(last_version.status, ObjectTypeVersionStatus.draft)

    def test_display_all_versions_in_history(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create_batch(3, object_type=object_type)
        url = reverse("admin:core_objecttype_history", args=[object_type.id])

        response = self.app.get(url)
        object_type = response.context["object"]

        self.assertEqual(response.status_code, 200)

        table = response.html.find(id="change-history")
        table_rows = table.tbody.find_all("tr")

        self.assertEqual(len(table_rows), 3)

        for object_version, row in zip(object_type.ordered_versions, table_rows):
            row_version = row.find("td")
            self.assertEqual(int(row_version.text), object_version.version)
