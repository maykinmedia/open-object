from django.test import TestCase, tag
from django.urls import reverse

from maykin_2fa.test import disable_admin_mfa
from maykin_common.vcr import VCRMixin

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import ObjectTypeFactory


@disable_admin_mfa()
class PermissionAdminTests(VCRMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create(superuser=True)
        self.client.force_login(self.user)
        self.url = reverse("admin:token_permission_add")

    @tag("#449")
    def test_with_object_types_api_v2(self):
        """
        Regression test for #449.
        Test if Permission admin can handle objecttypes API V2 which added pagination
        """
        object_type = ObjectTypeFactory.create(
            uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.context["adminform"].form
        choices = list(form.fields["object_type"].choices)

        self.assertEqual(
            str(choices[1][0].value),
            str(object_type.uuid),
        )
        self.assertEqual(
            choices[1][1],
            str(object_type),
        )

    @tag("gh-518")
    def test_object_type_choices_are_sorted_alphabetically(self):
        ObjectTypeFactory.create(name="Quokka")
        ObjectTypeFactory.create(name="Alpaca")
        ObjectTypeFactory.create(name="Bumblebee")

        response = self.client.get(self.url)
        choices = response.context["object_type_choices"]

        labels = [label for _, label in choices if label and label != "---------"]

        self.assertEqual(labels, sorted(labels))
