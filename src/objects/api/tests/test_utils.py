from datetime import date, datetime, time, timedelta

from django.test import TestCase

from ..utils import (
    is_date,
    is_datetime,
    is_duration,
    is_number,
    is_time,
    string_to_value,
)


class HelpersUtilsTestCase(TestCase):
    def test_string_to_value_numbers(self):
        self.assertEqual(string_to_value("42"), 42.0)
        self.assertEqual(string_to_value("3.14"), 3.14)
        self.assertEqual(string_to_value("-7.5"), -7.5)
        self.assertEqual(string_to_value("0"), 0.0)

    def test_string_to_value_datetime(self):
        result = string_to_value("2026-01-01T12:34:56")
        self.assertEqual(result, datetime(2026, 1, 1, 12, 34, 56))
        self.assertIsInstance(result, datetime)

        result = string_to_value("2026-01-01T12:34:56+00:00")
        self.assertIsInstance(result, datetime)

        result = string_to_value("2026-01-01T12:34:56")
        self.assertNotIsInstance(result, date.__class__)
        self.assertIsInstance(result, datetime)

    def test_string_to_value_date(self):
        result = string_to_value("2026-01-01")
        self.assertEqual(result, date(2026, 1, 1))
        self.assertIsInstance(result, date)
        self.assertNotIsInstance(result, datetime)

    def test_string_to_value_time(self):
        result = string_to_value("14:30:00")
        self.assertEqual(result, time(14, 30, 0))
        self.assertIsInstance(result, time)

        result = string_to_value("14:30:00+00:00")
        self.assertIsInstance(result, time)

        result = string_to_value("14:30:00.123456")
        self.assertIsInstance(result, time)

    def test_string_to_value_duration(self):
        result = string_to_value("P1D")
        self.assertEqual(result, timedelta(days=1))
        self.assertIsInstance(result, timedelta)

        result = string_to_value("PT4H30M")
        self.assertEqual(result, timedelta(hours=4, minutes=30))

        result = string_to_value("P1DT2H3M4S")
        self.assertIsInstance(result, timedelta)

        result = string_to_value("P14D")
        self.assertEqual(result, timedelta(weeks=2))

    def test_string_to_value_string(self):
        self.assertEqual(string_to_value("hello"), "hello")
        self.assertEqual(string_to_value(""), "")


class IsDatetimeTests(TestCase):
    def test_valid(self):
        for value in [
            "2026-01-01T12:34:56",
            "2026-01-01T12:34:56+02:00",
            "2026-01-01T00:00:00Z",
        ]:
            with self.subTest(value=value):
                self.assertTrue(is_datetime(value))

    def test_invalid(self):
        for value in [
            "not-a-datetime",
            "14:30:00",
            "",
        ]:
            with self.subTest(value=value):
                self.assertFalse(is_datetime(value))


class IsTimeTests(TestCase):
    def test_valid(self):
        for value in [
            "14:30:00",
            "14:30:00+00:00",
            "14:30:00.123456",
        ]:
            with self.subTest(value=value):
                self.assertTrue(is_time(value))

    def test_invalid(self):
        for value in [
            "25:00:00",
            "14:60:00",
            "2026-01-01",
            "not-a-time",
            "",
        ]:
            with self.subTest(value=value):
                self.assertFalse(is_time(value))


class IsDurationTests(TestCase):
    def test_valid(self):
        for value in [
            "P1D",
            "P14D",
            "PT4H30M",
            "P3DT4H5M6S",
            "PT30S",
        ]:
            with self.subTest(value=value):
                self.assertTrue(is_duration(value))

    def test_invalid(self):
        for value in [
            "1D",
            "not-a-duration",
            "2026-01-01",
        ]:
            with self.subTest(value=value):
                self.assertFalse(is_duration(value))


class IsDateTests(TestCase):
    def test_valid(self):
        for value in [
            "2026-01-01",
            "2000-12-31",
            "1990-06-15",
        ]:
            with self.subTest(value=value):
                self.assertTrue(is_date(value))

    def test_invalid(self):
        for value in [
            "not-a-date",
            "42",
            "14:30:00",
            "",
        ]:
            with self.subTest(value=value):
                self.assertFalse(is_date(value))


class IsNumberTests(TestCase):
    def test_valid(self):
        for value in [
            "42",
            "3.14",
            "-7",
            "0",
            "1e5",
        ]:
            with self.subTest(value=value):
                self.assertTrue(is_number(value))

    def test_invalid(self):
        for value in [
            "hello",
            "",
            "1.2.3",
            "1e",
            "abc",
        ]:
            with self.subTest(value=value):
                self.assertFalse(is_number(value))
