from django.db import connection
from django.test import TestCase


class PostgreSQLVersionTest(TestCase):
    def test_postgres_version(self):
        version = connection.pg_version  # pyright: ignore[reportAttributeAccessIssue]
        current_version = version // 10000
        min_supported_version = 15
        max_supported_version = 18
        assert min_supported_version <= current_version <= max_supported_version, (
            f"Unsupported PostgreSQL version {current_version}. "
            f"Supported versions: {min_supported_version} to {max_supported_version}."
        )
