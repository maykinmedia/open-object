import random
from datetime import date, timedelta

from django.contrib.gis.geos import Point

import factory
from factory.fuzzy import BaseFuzzyAttribute

from objects.core.constants import ReferenceType

from ..models import Object, ObjectRecord, ObjectType, ObjectTypeVersion, Reference


class ObjectTypeFactory(factory.django.DjangoModelFactory[ObjectType]):
    name = factory.Faker("word")
    name_plural = factory.LazyAttribute(lambda x: f"{x.name}s")
    description = factory.Faker("bs")

    class Meta:
        model = ObjectType


class ObjectTypeVersionFactory(factory.django.DjangoModelFactory[ObjectTypeVersion]):
    object_type = factory.SubFactory(ObjectTypeFactory)
    json_schema = factory.Dict(
        {
            "type": "object",
            "title": "Tree",
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "required": ["diameter"],
            "properties": {
                "diameter": {"type": "integer", "description": "size in cm."},
                "plantDate": {
                    "type": "string",
                    "format": "date",
                    "description": "Date the tree was planted.",
                },
            },
        }
    )

    class Meta:
        model = ObjectTypeVersion


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class ObjectDataFactory(factory.DictFactory):
    some_field = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    city = factory.Faker("city")
    description = factory.Faker("sentence")
    diameter = factory.LazyAttribute(lambda x: random.randrange(1, 10_000))


class ObjectFactory(factory.django.DjangoModelFactory[Object]):
    object_type = factory.SubFactory(ObjectTypeFactory)

    class Meta:
        model = Object


class ObjectRecordFactory(factory.django.DjangoModelFactory[ObjectRecord]):
    object = factory.SubFactory(ObjectFactory)
    version = factory.Sequence(lambda n: n)
    data = factory.SubFactory(ObjectDataFactory)
    start_at = factory.fuzzy.FuzzyDate(
        start_date=date.today() - timedelta(days=365),
        end_date=date.today(),
    )
    geometry = FuzzyPoint()

    class Meta:
        model = ObjectRecord


class ReferenceFactory(factory.django.DjangoModelFactory[Reference]):
    type = ReferenceType.zaak
    url = factory.Faker("url")
    record = factory.SubFactory(ObjectRecordFactory)

    class Meta:
        model = Reference
