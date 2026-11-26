from collections import defaultdict

from django.conf import settings
from django.db import models

from notifications_api_common.kanalen import KANAAL_REGISTRY, Kanaal
from rest_framework.request import Request

from objects.core.models import ObjectRecord
from objects.tests.v2.utils import reverse


class ObjectKanaal(Kanaal):
    def __init__(
        self,
        label: str,
        main_resource: models.base.ModelBase,
        kenmerken: tuple | None = None,
    ):
        self.label = label
        self.main_resource = main_resource

        self.usage = defaultdict(list)  # filled in by metaclass of notifications

        # check that we're refering to existing fields
        self.kenmerken = kenmerken or ()

        KANAAL_REGISTRY.add(self)

    def get_kenmerken(
        self,
        obj: models.Model,
        data: dict | None = None,
        request: Request | None = None,  # noqa
    ) -> dict:
        data = data or {}
        return {
            kenmerk: (
                data.get("type")
                or request.build_absolute_url(  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                    reverse("objecttype-detail", args=[data.object_type.uuid])  # pyright: ignore[reportAttributeAccessIssue]
                )
                if kenmerk == "object_type"
                else data.get(kenmerk, getattr(obj, kenmerk))
            )
            for kenmerk in self.kenmerken
        }

    @property
    def description(self):
        """For Objects endpoint main resource is ObjectRecord, so adjust info here"""
        kenmerk_template = "* `{kenmerk}`: {help_text}"
        main_resource = getattr(self.main_resource, "object").field.related_model
        kenmerken = [
            kenmerk_template.format(
                kenmerk=kenmerk,
                help_text=main_resource._meta.get_field(kenmerk).help_text,
            )
            for kenmerk in self.kenmerken
        ]

        description = (
            "**Main resource**\n\n"
            "`{options.model_name}`\n\n\n\n"
            "**Kenmerken**\n\n"
            "{kenmerken}"
        ).format(options=main_resource._meta, kenmerken="\n".join(kenmerken))

        return description


KANAAL_OBJECTEN = ObjectKanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=ObjectRecord,
    kenmerken=("object_type",),
)
