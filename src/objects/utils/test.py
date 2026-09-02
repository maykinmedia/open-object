from django.core.cache import caches

from rest_framework.test import APITestCase as APITestCaseDRF

from objects.token.tests.factories import TokenAuthFactory


class TokenAuthMixin(APITestCaseDRF):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.token_auth = TokenAuthFactory.create(
            contact_person="testsuite", email="test@letmein.nl"
        )

    def setUp(self):
        super().setUp()

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_auth.token}")


class ClearCachesMixin(APITestCaseDRF):
    def setUp(self):
        super().setUp()
        self._clear_caches()
        self.addCleanup(self._clear_caches)

    def _clear_caches(self):
        for cache in caches.all():
            cache.clear()
