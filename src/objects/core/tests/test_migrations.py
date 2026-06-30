import importlib
import threading
import time
from unittest.mock import patch

from django.test import override_settings

from objects.token.tests.test_migrations import BaseMigrationTest


class TestBackfillDenormalizedObjectType(BaseMigrationTest):
    app = "core"
    migrate_from = "0032_objectrecord__object_type"
    migrate_to = "0033_objectrecord__backfill_denormalized_fields"

    def test_denormalize_object_type_to_object_record(self):
        ObjectType = self.old_app_state.get_model("core", "ObjectType")
        Object = self.old_app_state.get_model("core", "Object")
        ObjectRecord = self.old_app_state.get_model("core", "ObjectRecord")
        Service = self.old_app_state.get_model("zgw_consumers", "Service")

        service = Service.objects.create(api_root="http://example.local:8001/api/v2/")

        object_type1 = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75", service=service
        )
        object_type2 = ObjectType.objects.create(
            uuid="89a30410-5d80-4007-a660-50dd94994464", service=service
        )
        object1 = Object.objects.create(object_type=object_type1)
        object2 = Object.objects.create(object_type=object_type2)
        ObjectRecord.objects.create(
            object=object1, index=1, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object1, index=2, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object2, index=1, version=1, start_at="2025-01-01"
        )

        self._perform_migration()

        ObjectRecord = self.apps.get_model("core", "ObjectRecord")

        records = ObjectRecord.objects.order_by("pk")

        self.assertEqual(records.count(), 3)

        record1, record2, record3 = records

        self.assertEqual(record1._object_type, record1.object.object_type, object_type1)
        self.assertEqual(record2._object_type, record2.object.object_type, object_type1)
        self.assertEqual(record3._object_type, record3.object.object_type, object_type2)

    def test_concurrently_inserted_records_are_normalized(self):
        ObjectType = self.old_app_state.get_model("core", "ObjectType")
        Object = self.old_app_state.get_model("core", "Object")
        ObjectRecord = self.old_app_state.get_model("core", "ObjectRecord")
        Service = self.old_app_state.get_model("zgw_consumers", "Service")

        service = Service.objects.create(api_root="http://example.local:8001/api/v2/")

        object_type1 = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75", service=service
        )
        object_type2 = ObjectType.objects.create(
            uuid="89a30410-5d80-4007-a660-50dd94994464", service=service
        )
        object1 = Object.objects.create(object_type=object_type1)
        object2 = Object.objects.create(object_type=object_type2)
        ObjectRecord.objects.create(
            object=object1, index=1, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object1, index=2, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object2, index=1, version=1, start_at="2025-01-01"
        )

        migration_module = importlib.import_module(
            "objects.core.migrations.0033_objectrecord__backfill_denormalized_fields"
        )

        original_batch = migration_module.backfill_object_type_batch_concurrent

        def delayed_batch(cursor):
            time.sleep(0.1)  # simulate long-running batch
            return original_batch(cursor)

        with patch.object(
            migration_module,
            "backfill_object_type_batch_concurrent",
            side_effect=delayed_batch,
        ):
            thread = threading.Thread(target=self._perform_migration)
            thread.start()

            # Simultaneously insert a new record
            ObjectRecord.objects.create(
                object=object2,
                index=2,
                version=1,
                start_at="2025-01-01",
                _object_type=None,
            )

            thread.join()

        ObjectRecord = self.apps.get_model("core", "ObjectRecord")

        records = ObjectRecord.objects.order_by("pk")

        self.assertEqual(records.count(), 4)

        record1, record2, record3, record4 = records

        self.assertEqual(record1._object_type, record1.object.object_type, object_type1)
        self.assertEqual(record2._object_type, record2.object.object_type, object_type1)
        self.assertEqual(record3._object_type, record3.object.object_type, object_type2)
        # Assert that the inserted row was also backfilled
        self.assertEqual(record4._object_type, record4.object.object_type, object_type2)


class TestBackfillStrictFormatChecker(BaseMigrationTest):
    app = "core"
    migrate_from = "0039_alter_objecttype_unique_together_and_more"
    migrate_to = "0040_objecttypeversion_strict_format_checker"

    def test_existing_records_are_set_to_false(self):
        ObjectType = self.old_app_state.get_model("core", "ObjectType")
        ObjectTypeVersion = self.old_app_state.get_model("core", "ObjectTypeVersion")
        object_type = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75"
        )

        ObjectTypeVersion.objects.create(object_type=object_type, version=1)
        ObjectTypeVersion.objects.create(object_type=object_type, version=2)
        ObjectTypeVersion.objects.create(object_type=object_type, version=3)

        self._perform_migration()

        ObjectTypeVersion = self.apps.get_model("core", "ObjectTypeVersion")

        versions = ObjectTypeVersion.objects.order_by("pk")
        self.assertEqual(versions.count(), 3)

        for version in versions:
            self.assertFalse(version.strict_format_checker)

    def test_field_is_set_from_settings_after_migration(self):
        self._perform_migration()

        from objects.core.models import ObjectType, ObjectTypeVersion

        object_type = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75"
        )

        with override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=True):
            version = ObjectTypeVersion.objects.create(
                object_type=object_type, version=1
            )
            version.refresh_from_db()
            self.assertTrue(version.strict_format_checker)

        with override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=False):
            version = ObjectTypeVersion.objects.create(
                object_type=object_type, version=2
            )
            version.refresh_from_db()
            self.assertFalse(version.strict_format_checker)
