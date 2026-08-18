import uuid
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import TestCase, override_settings

from upgrade_check.models import Version

from objects.core.tests.factories import ObjectTypeFactory
from objects.token.tests.test_migrations import BaseMigrationTest


class TestUpgradeCheckBefore40(BaseMigrationTest):
    app = "core"
    migrate_from = "0036_objecttype_is_imported"
    migrate_to = "0037_reference"

    def setUp(self):
        super().setUp()

        self.ObjectType = self.old_app_state.get_model("core", "ObjectType")
        Service = self.old_app_state.get_model("zgw_consumers", "Service")

        self.service = Service.objects.create()

        # patch get_model in command to return the model with is_imported
        self.patch = patch(
            "objects.core.management.commands.check_for_external_objecttypes.Command._get_objecttype",
            return_value=self.ObjectType,
        ).start()

    def tearDown(self):
        self.patch.stop()

    @override_settings(RELEASE="4.0.0")
    def test_upgrade_from_30_to_40(self):
        """
        from 3.0.0 directly to 4.0.0 is not allowed, 3.6.1 is the minimum version

        """
        Version.objects.create(version="3.0.0", git_sha="test")

        with self.assertRaises(SystemCheckError):
            call_command("check")

    @override_settings(RELEASE="4.0.0")
    def test_upgrade_from_36_to_40_with_non_imported_objecttypes(self):
        """
        import should fail because non-imported objecttypes exist
        """
        Version.objects.create(version="3.6.1", git_sha="test")
        self.ObjectType.objects.create(
            is_imported=False, uuid=uuid.uuid4(), service=self.service
        )

        with self.assertRaises(SystemCheckError):
            call_command("check")

    @override_settings(RELEASE="4.0.0")
    def test_upgrade_from_36_to_40_with_all_imported(self):
        """
        import should succeed because all objecttypes are imported
        """
        Version.objects.create(version="3.6.1", git_sha="test")
        self.ObjectType.objects.create(
            is_imported=True, uuid=uuid.uuid4(), service=self.service
        )

        call_command("check")

    @override_settings(RELEASE="4.1.0")
    def test_upgrade_from_37_to_41_with_non_imported_objecttypes(self):
        """
        import should fail because non-imported objecttypes exist
        """
        Version.objects.create(version="3.7.0", git_sha="test")
        self.ObjectType.objects.create(
            is_imported=False, uuid=uuid.uuid4(), service=self.service
        )

        with self.assertRaises(SystemCheckError):
            call_command("check")

    @override_settings(RELEASE="4.1.0")
    def test_upgrade_from_37_to_41_with_all_imported(self):
        """
        import should succeed because all objecttypes are imported
        """
        Version.objects.create(version="3.7.0", git_sha="test")
        self.ObjectType.objects.create(
            is_imported=True, uuid=uuid.uuid4(), service=self.service
        )

        call_command("check")


class TestUpgradeCheckAfter40(TestCase):
    @override_settings(RELEASE="4.0.0")
    def test_upgrade_from_36_to_40_with_non_imported(self):
        Version.objects.create(version="3.6.1", git_sha="test")
        ObjectTypeFactory.create(is_imported=False)

        with self.assertRaises(SystemCheckError):
            call_command("check")

    @override_settings(RELEASE="4.0.0")
    def test_upgrade_from_36_to_40_with_imported(self):
        Version.objects.create(version="3.6.1", git_sha="test")
        ObjectTypeFactory.create(is_imported=True)

        call_command("check")

    @override_settings(RELEASE="4.1.0")
    def test_upgrade_from_40_to_41_with_all_imported(self):
        """
        import should succeed because version is already 4.0.0
        """
        Version.objects.create(version="4.0.0", git_sha="test")
        ObjectTypeFactory.create()
        call_command("check")
