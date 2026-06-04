from django.test import override_settings, tag

from maykin_2fa.test import disable_admin_mfa
from playwright.sync_api import expect

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import ObjectTypeFactory, ObjectTypeVersionFactory
from objects.tests.playwright import PlaywrightSyncLiveServerTestCase
from objects.token.tests.factories import PermissionFactory, TokenAuthFactory


@tag("playwright")
@override_settings(AXES_ENABLED=False)
@disable_admin_mfa()
class PermissionAdminTests(PlaywrightSyncLiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(superuser=True)
        self.user.set_password("secret")
        self.user.save()

        self.login_state = self.get_user_login_state(self.user)

    def test_field_based_authorization_fetches_versions(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(
            object_type=object_type,
            version=1,
            json_schema={
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"},
                },
            },
        )

        token = TokenAuthFactory.create()

        context = self.browser.new_context(storage_state=self.login_state)
        page = context.new_page()

        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"BROWSER EXCEPTION: {exc}"))

        page.goto(self.live_reverse("admin:token_permission_add"))

        page.wait_for_selector("#id_token_auth", timeout=15000)
        page.select_option("#id_token_auth", str(token.pk))

        page.locator("#id_object_type").click()
        page.locator("#id_object_type").fill(str(object_type))

        page.get_by_role("option", name=str(object_type)).click()
        page.select_option("#id_mode", "read_only")

        expect(page.locator("#id_use_fields")).to_be_enabled(timeout=5000)
        page.check("#id_use_fields")

        expect(page.locator("text=field1")).to_be_visible(timeout=5000)
        expect(page.locator("text=field2")).to_be_visible(timeout=5000)

        page.get_by_label("field1").check()
        page.get_by_label("field2").check()

        page.locator("input[name='_save']").click()

        page.wait_for_selector(".messagelist", timeout=10000)

        from objects.token.models import Permission

        permission = Permission.objects.get(token_auth=token, object_type=object_type)

        assert permission.use_fields is True

        assert "record__data__field1" in permission.fields["1"]
        assert "record__data__field2" in permission.fields["1"]

        context.close()

    def test_edit_existing_permission_shows_fields(self):
        object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(
            object_type=object_type,
            version=1,
            json_schema={
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"},
                },
            },
        )

        token = TokenAuthFactory.create()
        permission = PermissionFactory.create(
            token_auth=token,
            object_type=object_type,
            mode="read_only",
            use_fields=True,
        )

        context = self.browser.new_context(storage_state=self.login_state)
        page = context.new_page()

        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"BROWSER EXCEPTION: {exc}"))

        page.goto(
            self.live_reverse(
                "admin:token_permission_change",
                args=[permission.pk],
            )
        )

        page.wait_for_selector("#id_token_auth", timeout=15000)

        expect(page.locator("#id_token_auth")).to_have_value(str(token.pk))
        expect(page.locator('input[type="hidden"][name="object_type"]')).to_have_value(
            str(object_type.uuid)
        )

        expect(page.locator("#id_use_fields")).to_be_checked()

        expect(page.locator("text=field1")).to_be_visible(timeout=5000)
        expect(page.locator("text=field2")).to_be_visible(timeout=5000)

        context.close()
