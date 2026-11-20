from typing import TYPE_CHECKING
from uuid import UUID

from django_setup_configuration.fields import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel

from objects.core.models import ObjectType


class ObjectTypeConfigurationModel(ConfigurationModel):
    if TYPE_CHECKING:
        uuid: UUID

    name: str = DjangoModelRef(ObjectType, "name")

    class Meta:
        django_model_refs = {ObjectType: ("uuid",)}


class ObjectTypesConfigurationModel(ConfigurationModel):
    items: list[ObjectTypeConfigurationModel]
