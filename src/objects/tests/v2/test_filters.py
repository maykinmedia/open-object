import os
from datetime import date, timedelta
from unittest.mock import patch

from django.db.utils import ProgrammingError

from furl import furl
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import get_validation_errors

from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ...core.constants import DataClassificationChoices
from .utils import reverse, reverse_lazy


class FilterObjectTypeTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        cls.another_object_type = ObjectTypeFactory.create()

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )
        PermissionFactory.create(
            object_type=cls.another_object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_object_type(self):
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object)
        ObjectFactory.create(object_type=self.another_object_type)

        response = self.client.get(
            self.url,
            {
                "type": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )

    def test_filter_invalid_objecttype(self):
        response = self.client.get(self.url, {"type": "invalid-objecttype-url"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "type")

        self.assertEqual(error["reason"], "Invalid value.")
        self.assertEqual(error["code"], "invalid")

    def test_filter_too_long_object_type(self):
        response = self.client.get(
            self.url,
            {
                "type": f"https://testserver/{'a' * 1000}/{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "type")

        self.assertEqual(error["code"], "max_length")
        self.assertEqual(error["reason"], "The value has too many characters")


class FilterDataAttrsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_exact_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "name__exact__demo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_number(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "diameter__exact__4"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_date(self):
        record = ObjectRecordFactory.create(
            data={"date": "2000-11-01"}, object__object_type=self.object_type
        )

        response = self.client.get(self.url, {"data_attrs": "date__exact__2000-11-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_datetime(self):
        record = ObjectRecordFactory.create(
            data={"startdatetime": "2026-01-01T08:00:00"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"startdatetime": "2026-06-01T18:00:00"},
            object__object_type=self.object_type,
        )

        response = self.client.get(
            self.url, {"data_attrs": "startdatetime__exact__2026-01-01T08:00:00"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_duration(self):
        record = ObjectRecordFactory.create(
            data={"duration": "P1D"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"duration": "P7D"},
            object__object_type=self.object_type,
        )

        response = self.client.get(self.url, {"data_attrs": "duration__exact__P1D"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_time(self):
        record = ObjectRecordFactory.create(
            data={"startdatetime": "08:00:00"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"startdatetime": "18:00:00"},
            object__object_type=self.object_type,
        )

        response = self.client.get(
            self.url, {"data_attrs": "startdatetime__exact__08:00:00"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte(self):
        record1 = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        record2 = ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "diameter__lte__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        data = sorted(data, key=lambda x: x["record"]["data"]["diameter"])

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record1.object.uuid])}",
        )
        self.assertEqual(
            data[1]["url"],
            f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
        )

    def test_filter_lt(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "diameter__lt__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte_not_numerical(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__lt__value"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Operator `lt` supports only dates and/or numeric values",
        )

    def test_filter_lte_date(self):
        record = ObjectRecordFactory.create(
            data={"date": "2000-11-01"}, object__object_type=self.object_type
        )

        response = self.client.get(self.url, {"data_attrs": "date__lte__2000-12-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

        response = self.client.get(self.url, {"data_attrs": "date__lte__2000-10-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 0)

        response = self.client.get(self.url, {"data_attrs": "date__lte__2000-11-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_datetime_comparisons(self):
        record_early = ObjectRecordFactory.create(
            data={"startdatetime": "2026-01-01T08:00:00"},
            object__object_type=self.object_type,
        )
        record_late = ObjectRecordFactory.create(
            data={"startdatetime": "2026-06-01T18:00:00"},
            object__object_type=self.object_type,
        )

        early_url = f"http://testserver{reverse('object-detail', args=[record_early.object.uuid])}"
        late_url = f"http://testserver{reverse('object-detail', args=[record_late.object.uuid])}"

        with self.subTest("gt"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__gt__2026-01-01T08:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()["results"]
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["url"], late_url)

        with self.subTest("gte"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__gte__2026-01-01T08:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 2)

        with self.subTest("lt"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__lt__2026-06-01T18:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()["results"]
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["url"], early_url)

        with self.subTest("lte"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__lte__2026-06-01T18:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 2)

    def test_filter_time_comparisons(self):
        record_early = ObjectRecordFactory.create(
            data={"startdatetime": "08:00:00"},
            object__object_type=self.object_type,
        )
        record_late = ObjectRecordFactory.create(
            data={"startdatetime": "18:00:00"},
            object__object_type=self.object_type,
        )

        early_url = f"http://testserver{reverse('object-detail', args=[record_early.object.uuid])}"
        late_url = f"http://testserver{reverse('object-detail', args=[record_late.object.uuid])}"

        with self.subTest("gt"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__gt__08:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()["results"]
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["url"], late_url)

        with self.subTest("gte"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__gte__08:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 2)

        with self.subTest("lt"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__lt__18:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()["results"]
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["url"], early_url)

        with self.subTest("lte"):
            response = self.client.get(
                self.url, {"data_attrs": "startdatetime__lte__18:00:00"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 2)

    def test_filter_invalid_operator(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__not__value"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Comparison operator `not` is unknown",
        )
        self.assertEqual(error["code"], "invalid-data-attrs-query")

    def test_filter_invalid_param(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__exact"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Filter expression 'diameter__exact' doesn't have the shape 'key__operator__value'",
        )
        self.assertEqual(error["code"], "invalid-data-attrs-query")

    def test_filter_nested_attr(self):
        record = ObjectRecordFactory.create(
            data={"dimensions": {"unrelated_field": 1, "diameter": 4}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"unrelated_field": 1, "diameter": 5}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"unrelated_field": 1, "diameter": 4},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(
            self.url, {"data_attrs": "dimensions__diameter__exact__4"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_comma_separated(self):
        record = ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}, "name": "demo"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 5}, "name": "demo"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}, "name": "other"},
            object__object_type=self.object_type,
        )

        response = self.client.get(
            self.url, {"data_attrs": "dimensions__diameter__exact__4,name__exact__demo"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_icontains_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "Something important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "Nothing important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "name__icontains__some"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_icontains_numeric(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 45}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attrs": "diameter__icontains__4"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exclude_old_records(self):
        record_old = ObjectRecordFactory.create(
            data={"diameter": 45},
            object__object_type=self.object_type,
            start_at=date.today() - timedelta(days=10),
            end_at=date.today() - timedelta(days=1),
        )
        ObjectRecordFactory.create(
            data={"diameter": 50}, object=record_old.object, start_at=record_old.end_at
        )

        response = self.client.get(self.url, {"data_attrs": "diameter__exact__45"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 0)

    def test_filter_date_field_gte(self):
        ObjectRecordFactory.create(
            data={"dateField": "2000-10-10"}, object__object_type=self.object_type
        )

        response = self.client.get(
            self.url, {"data_attrs": "dateField__gte__2000-10-10"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)

        response = self.client.get(
            self.url, {"data_attrs": "dateField__gte__2000-10-11"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 0)

    def test_filter_in_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo1"}, object__object_type=self.object_type
        )
        record2 = ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "demo3"}, object__object_type=self.object_type
        )

        response = self.client.get(self.url, {"data_attrs": "name__in__demo1|demo2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
        )
        self.assertEqual(
            data[1]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )


class FilterDataAttrTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_exact_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "name__exact__demo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_number(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "diameter__exact__4"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_date(self):
        record = ObjectRecordFactory.create(
            data={"date": "2000-11-01"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"date": "2020-11-01"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "date__exact__2000-11-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte(self):
        record1 = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        record2 = ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "diameter__lte__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        data = sorted(data, key=lambda x: x["record"]["data"]["diameter"])

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record1.object.uuid])}",
        )
        self.assertEqual(
            data[1]["url"],
            f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
        )

    def test_filter_lt(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "diameter__lt__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte_not_numerical(self):
        response = self.client.get(self.url, {"data_attr": "diameter__lt__value"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            "Operator `lt` supports only dates and/or numeric values", error["reason"]
        )

    def test_filter_lte_date(self):
        record = ObjectRecordFactory.create(
            data={"date": "2000-11-01"}, object__object_type=self.object_type
        )

        response = self.client.get(self.url, {"data_attr": "date__lte__2000-12-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

        response = self.client.get(self.url, {"data_attr": "date__lte__2000-10-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 0)

        response = self.client.get(self.url, {"data_attr": "date__lte__2000-11-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_invalid_operator(self):
        response = self.client.get(self.url, {"data_attr": "diameter__not__value"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Comparison operator `not` is unknown",
        )

    def test_filter_invalid_param(self):
        response = self.client.get(self.url, {"data_attr": "diameter__exact"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Filter expression 'diameter__exact' doesn't have the shape 'key__operator__value'",
        )

    def test_filter_nested_attr(self):
        record = ObjectRecordFactory.create(
            data={"dimensions": {"unrelated_field": 1, "diameter": 4}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"unrelated_field": 1, "diameter": 5}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"unrelated_field": 1, "diameter": 4},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(
            self.url, {"data_attr": "dimensions__diameter__exact__4"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_icontains_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "Something important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "Nothing important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "name__icontains__some"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_icontains_numeric(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 45}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_attr": "diameter__icontains__4"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exclude_old_records(self):
        record_old = ObjectRecordFactory.create(
            data={"diameter": 45},
            object__object_type=self.object_type,
            start_at=date.today() - timedelta(days=10),
            end_at=date.today() - timedelta(days=1),
        )
        ObjectRecordFactory.create(
            data={"diameter": 50}, object=record_old.object, start_at=record_old.end_at
        )

        response = self.client.get(self.url, {"data_attr": "diameter__exact__45"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 0)

    def test_filter_date_field_gte(self):
        ObjectRecordFactory.create(
            data={"dateField": "2000-10-10"}, object__object_type=self.object_type
        )

        response = self.client.get(
            self.url, {"data_attr": "dateField__gte__2000-10-10"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)

        response = self.client.get(
            self.url, {"data_attr": "dateField__gte__2000-10-11"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 0)

    def test_filter_in_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo1"}, object__object_type=self.object_type
        )
        record2 = ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "demo3"}, object__object_type=self.object_type
        )

        response = self.client.get(self.url, {"data_attr": "name__in__demo1|demo2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
        )
        self.assertEqual(
            data[1]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_icontains_string_with_comma(self):
        """
        regression test for https://github.com/maykinmedia/open-object/issues/472
        """
        ObjectRecordFactory.create(
            data={"name": "Something important"}, object__object_type=self.object_type
        )
        record = ObjectRecordFactory.create(
            data={"name": "Advies, support en kennis om te weten"},
            object__object_type=self.object_type,
        )

        response = self.client.get(
            self.url, {"data_attr": "name__icontains__Advies, support en kennis"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_two_icontains_with_comma(self):
        """
        regression test for https://github.com/maykinmedia/open-object/issues/472
        """
        ObjectRecordFactory.create(
            data={"name": "Something important"}, object__object_type=self.object_type
        )
        record = ObjectRecordFactory.create(
            data={"name": "Advies, support en kennis om te weten"},
            object__object_type=self.object_type,
        )
        url = (
            furl(self.url)
            .add({"data_attr": "name__icontains__Advies, support en kennis"})
            .add({"data_attr": "name__icontains__om"})
            .url
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_comma_separated_invalid(self):
        response = self.client.get(
            self.url,
            {"data_attr": "dimensions__diameter__exact__4,name__exact__demo"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "")

        self.assertEqual(
            error["reason"],
            "Filter expression 'dimensions__diameter__exact__4,name__exact__demo' "
            "must have the shape 'key__operator__value', commas can only be present in "
            "the 'value'",
        )
        self.assertEqual(error["code"], "invalid-data-attr-query")


class FilterDateTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_date_detail(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record1 = ObjectRecordFactory.create(
            object=object, start_at="2020-01-01", end_at="2020-12-31"
        )
        ObjectRecordFactory.create(object=object, start_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"date": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["record"]["index"], record1.index)

    def test_filter_date_detail_no_actual_record(self):
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object, start_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"date": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_date_list(self):
        # object 1 - show
        object1 = ObjectFactory.create(object_type=self.object_type)
        record11 = ObjectRecordFactory.create(
            object=object1, start_at="2020-01-01", end_at="2020-12-31"
        )
        ObjectRecordFactory.create(object=object1, start_at="2021-01-01")
        # object 2 - don't show
        ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at="2021-01-01"
        )

        url = reverse_lazy("object-list")

        response = self.client.get(url, {"date": "2020-07-01"})

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object1.uuid])}",
        )
        self.assertEqual(data[0]["record"]["index"], record11.index)

    def test_filter_registration_date_detail(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record1 = ObjectRecordFactory.create(
            object=object,
            registration_at="2020-01-01",
        )
        ObjectRecordFactory.create(object=object, registration_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["record"]["index"], record1.index)

    def test_filter_registration_date_detail_no_record(self):
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object, registration_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_registration_date_list(self):
        # object 1 - show
        object1 = ObjectFactory.create(object_type=self.object_type)
        record11 = ObjectRecordFactory.create(
            object=object1, registration_at="2020-01-01"
        )
        ObjectRecordFactory.create(object=object1, registration_at="2021-01-01")
        # object 2 - don't show
        ObjectRecordFactory.create(
            object__object_type=self.object_type, registration_at="2021-01-01"
        )

        url = reverse_lazy("object-list")

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object1.uuid])}",
        )
        self.assertEqual(data[0]["record"]["index"], record11.index)

    def test_filter_on_both_date_and_registration_date(self):
        url = reverse_lazy("object-list")
        response = self.client.get(
            url,
            {"date": "2020-07-01", "registrationDate": "2020-08-01"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(
            data["invalid_params"][0]["reason"],
            "'date' and 'registrationDate' parameters can't be used in the same request",
        )


class FilterDataIcontainsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_without_nesting(self):
        record = ObjectRecordFactory.create(
            data={"name": "Something important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "Nothing important"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_icontains": "some"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_with_nesting(self):
        record = ObjectRecordFactory.create(
            data={"person": {"name": "Something important"}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"person": {"name": "Nothing important"}},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

        response = self.client.get(self.url, {"data_icontains": "some"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    @patch.dict(os.environ, {"DEBUG": "false"})
    @patch(
        "objects.core.query.ObjectRecordQuerySet._fetch_all",
        side_effect=ProgrammingError("'jsonpath' is not found"),
    )
    def test_filter_db_error(self, mock_query):
        response = self.client.get(self.url, {"data_icontains": "some"})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()

        data.pop("instance", None)

        self.assertEqual(
            data,
            {
                "code": "search-not-supported",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "This search operation is not supported by the underlying data store.",
                "type": "http://testserver/ref/fouten/ProgrammingError/",
            },
        )


class FilterTypeVersionTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

        cls.record_v1 = ObjectRecordFactory.create(
            data={"person": {"name": "Something important"}},
            object__object_type=cls.object_type,
            version=1,
        )

        cls.record_v2 = ObjectRecordFactory.create(
            data={"person": {"name": "Something important"}},
            object__object_type=cls.object_type,
            version=2,
        )

    def test_filter_existing_version(self):
        response = self.client.get(self.url, {"typeVersion": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["record"]["typeVersion"], 1)

    def test_filter_unkown_version(self):
        response = self.client.get(self.url, {"typeVersion": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 0)


class ObjectTypeFilterTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("objecttype-list")

    def test_filter_public_data(self):
        object_type_1 = ObjectTypeFactory.create(
            data_classification=DataClassificationChoices.open
        )
        ObjectTypeFactory.create(data_classification=DataClassificationChoices.intern)

        response = self.client.get(
            self.url, {"dataClassification": DataClassificationChoices.open}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('objecttype-detail', args=[object_type_1.uuid])}",
        )
