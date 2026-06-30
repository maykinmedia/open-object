from __future__ import annotations

import datetime
import uuid
from typing import ClassVar

from django.conf import settings
from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    DataClassificationChoices,
    ObjectTypeVersionStatus,
    ReferenceType,
    UpdateFrequencyChoices,
)
from .query import ObjectQuerySet, ObjectRecordQuerySet, ObjectTypeQuerySet
from .utils import check_json_schema, check_objecttype


class ObjectType(models.Model):
    uuid = models.UUIDField(
        help_text=_("Unique identifier (UUID4)"),
        unique=True,
        default=uuid.uuid4,
    )

    is_imported = models.BooleanField(
        _("Is imported"),
        default=False,
        editable=False,
    )  # TODO temp field to track if object was imported, can be removed after objecttype migration (in 4.1.0)

    name = models.CharField(
        _("name"),
        max_length=100,
        help_text=_("Name of the object type"),
    )

    name_plural = models.CharField(
        _("name plural"),
        max_length=100,
        help_text=_("Plural name of the object type"),
    )
    description = models.CharField(
        _("description"),
        max_length=1000,
        blank=True,
        help_text=_("The description of the object type"),
    )
    data_classification = models.CharField(
        _("data classification"),
        max_length=50,
        choices=DataClassificationChoices.choices,
        default=DataClassificationChoices.open,
        help_text=_("Confidential level of the object type"),
    )
    maintainer_organization = models.CharField(
        _("maintainer organization"),
        max_length=200,
        blank=True,
        help_text=_("Organization which is responsible for the object type"),
    )
    maintainer_department = models.CharField(
        _("maintainer department"),
        max_length=200,
        blank=True,
        help_text=_("Business department which is responsible for the object type"),
    )
    contact_person = models.CharField(
        _("contact person"),
        max_length=200,
        blank=True,
        help_text=_(
            "Name of the person in the organization who can provide information about the object type"
        ),
    )
    contact_email = models.CharField(
        _("contact email"),
        max_length=200,
        blank=True,
        help_text=_(
            "Email of the person in the organization who can provide information about the object type"
        ),
    )
    source = models.CharField(
        _("source"),
        max_length=200,
        blank=True,
        help_text=_("Name of the system from which the object type originates"),
    )
    update_frequency = models.CharField(
        _("update frequency"),
        max_length=10,
        choices=UpdateFrequencyChoices.choices,
        default=UpdateFrequencyChoices.unknown,
        help_text=_("Indicates how often the object type is updated"),
    )
    provider_organization = models.CharField(
        _("provider organization"),
        max_length=200,
        blank=True,
        help_text=_(
            "Organization which is responsible for publication of the object type"
        ),
    )
    documentation_url = models.URLField(
        _("documentation url"),
        blank=True,
        help_text=_("Link to the documentation for the object type"),
    )
    labels = models.JSONField(
        _("labels"),
        help_text=_("Key-value pairs of keywords related for the object type"),
        default=dict,
        blank=True,
    )
    created_at = models.DateField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Date when the object type was created"),
    )
    modified_at = models.DateField(
        _("modified at"),
        auto_now=True,
        help_text=_("Last date when the object type was modified"),
    )
    allow_geometry = models.BooleanField(
        _("allow geometry"),
        default=True,
        help_text=_(
            "Shows whether the related objects can have geographic coordinates. "
            "If the value is 'false' the related objects are not allowed to "
            "have coordinates and the creation/update of objects with "
            "`geometry` property will raise an error "
        ),
    )

    objects = ObjectTypeQuerySet.as_manager()
    versions: models.QuerySet[ObjectTypeVersion]

    def __str__(self):
        return f"{self.name}"

    @property
    def last_version(self):
        if not self.versions:
            return None

        return self.versions.order_by("-version").first()

    @property
    def has_format_checker(self):
        if not self.last_version:
            return False

        return bool(self.last_version.strict_format_checker)

    @property
    def ordered_versions(self):
        return self.versions.order_by("-version")


class ObjectTypeVersion(models.Model):
    object_type = models.ForeignKey(
        ObjectType, on_delete=models.CASCADE, related_name="versions"
    )
    version = models.PositiveSmallIntegerField(
        _("version"), help_text=_("Integer version of the OBJECTTYPE")
    )
    created_at = models.DateField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Date when the version was created"),
    )
    modified_at = models.DateField(
        _("modified at"),
        auto_now=True,
        help_text=_("Last date when the version was modified"),
    )
    published_at = models.DateField(
        _("published_at"),
        null=True,
        blank=True,
        help_text=_("Date when the version was published"),
    )
    json_schema = models.JSONField(
        _("JSON schema"), help_text=_("JSON schema for Object validation"), default=dict
    )
    strict_format_checker = models.BooleanField(
        null=True,
        help_text=_(
            "When enabled, JSON Schema validation enforces format constraints. "
            "Defaults to the JSONSCHEMA_USE_FORMAT_CHECKER setting."
        ),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ObjectTypeVersionStatus.choices,
        default=ObjectTypeVersionStatus.draft,
        help_text=_("Status of the object type version"),
    )

    class Meta:
        unique_together = ("object_type", "version")

    def __str__(self):
        return f"{self.object_type} v.{self.version}"

    def clean(self):
        super().clean()

        check_json_schema(self.json_schema)

    def save(self, *args, **kwargs):
        if self.strict_format_checker is None:
            self.strict_format_checker = settings.JSONSCHEMA_USE_FORMAT_CHECKER

        if not self.version:
            self.version = self.generate_version_number()

        # save published_at
        previous_status = (
            ObjectTypeVersion.objects.get(id=self.id).status if self.id else None
        )
        if (
            self.status == ObjectTypeVersionStatus.published
            and previous_status != self.status
        ):
            self.published_at = datetime.date.today()

        super().save(*args, **kwargs)

    def generate_version_number(self) -> int:
        # XXX: this is racing other queries!
        existed_versions = ObjectTypeVersion.objects.filter(
            object_type=self.object_type
        )

        max_version = 0
        if existed_versions.exists():
            max_version = existed_versions.aggregate(models.Max("version"))[
                "version__max"
            ]

        version_number = max_version + 1
        if version_number > 32767:  # Postgrest has no USMALLINT, only SMALLINT
            raise ValidationError(
                _("Maximum version number 32767 has been reached for this objecttype")
            )
        return version_number


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text=_("Unique identifier (UUID4)")
    )
    object_type = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
        help_text=_("OBJECTTYPE"),
    )

    created_on = models.DateTimeField(auto_now_add=True, help_text=_("Creation date"))
    modified_on = models.DateTimeField(
        auto_now=True, help_text=_("Last modification date")
    )

    objects = ObjectQuerySet.as_manager()
    records: ClassVar[ObjectRecordQuerySet]

    @property
    def current_record(self) -> ObjectRecord | None:
        return self.records.filter_for_date(datetime.date.today()).first()

    @property
    def last_record(self) -> ObjectRecord | None:
        return self.records.order_by("-index").first()

    @property
    def record(self) -> ObjectRecord | None:
        # `actual_records` attribute is set in ObjectViewSet.get_queryset
        if getattr(self, "actual_records", None):
            return self.actual_records[0]

        # for create and update
        return self.current_record


class ObjectRecord(models.Model):
    index = models.PositiveIntegerField(
        default=1,
        help_text=_("Incremental index number of the object record."),
    )
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name="records")
    version = models.PositiveSmallIntegerField(
        _("version"),
        help_text=_("Version of the OBJECTTYPE for data in the object record"),
    )
    data = models.JSONField(
        _("data"),
        help_text=_("Object data, based on OBJECTTYPE"),
        default=dict,
        encoder=DjangoJSONEncoder,
    )
    start_at = models.DateField(
        _("start at"), help_text=_("Legal start date of the object record")
    )
    end_at = models.DateField(
        _("end at"), null=True, help_text=_("Legal end date of the object record")
    )
    registration_at = models.DateField(
        _("registration at"),
        default=datetime.date.today,
        help_text=_("The date when the record was registered in the system"),
    )
    correct = models.OneToOneField(
        "core.ObjectRecord",
        verbose_name="correction for",
        on_delete=models.CASCADE,
        related_name="corrected",
        null=True,
        blank=True,
        help_text=_("Object record which corrects the current record"),
    )
    geometry = GeometryField(
        _("geometry"),
        blank=True,
        null=True,
        help_text=_(
            "Point, linestring or polygon object which represents the coordinates of the "
            "object. Geometry can be added only if the related OBJECTTYPE allows this "
            "(`OBJECTTYPE.allowGeometry = true` or `OBJECTTYPE.allowGeometry` doesn't "
            "exist)"
        ),
    )

    created_on = models.DateTimeField(auto_now_add=True, help_text=_("Creation date"))
    modified_on = models.DateTimeField(
        auto_now=True, help_text=_("Last modification date")
    )

    # Denormalized field to avoid unnecessary joins on `Object`
    _object_type = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
        help_text=_("OBJECTTYPE"),
        null=False,
        blank=False,
        db_index=True,
    )

    objects = ObjectRecordQuerySet.as_manager()
    references: ClassVar[models.QuerySet[Reference]]

    class Meta:
        unique_together = ("object", "index")
        indexes = [
            GinIndex(fields=["data"], name="idx_objectrecord_data_gin"),
            models.Index(
                fields=["_object_type_id", "-index"],
                name="idx_objectrecord_type_index",
            ),
            models.Index(
                fields=["_object_type_id", "id"],
                name="idx_objectrecord_type_id",
            ),
            models.Index(
                fields=["_object_type_id", "start_at", "end_at", "object", "-index"],
                name="idx_type_start_end_object_idx",
            ),
        ]

    def __str__(self):
        return f"{self.version} ({self.start_at})"

    def clean(self):
        super().clean()

        if hasattr(self.object, "object_type") and self.version and self.data:
            check_objecttype(self.object.object_type, self.version, self.data)

    def save(self, *args, **kwargs):
        if not self.id and self.object.last_record:
            self.index = self.object.last_record.index + 1

            #  add end_at to previous record
            previous_record = self.object.last_record
            previous_record.end_at = self.start_at
            previous_record.save()

        self._object_type = self.object.object_type

        super().save(*args, **kwargs)


class Reference(models.Model):
    record = models.ForeignKey(
        ObjectRecord, on_delete=models.CASCADE, related_name="references"
    )
    type = models.CharField(
        max_length=4, choices=ReferenceType.choices, null=False, blank=False
    )
    url = models.URLField()

    class Meta:
        indexes = [models.Index(fields=["url"])]
        constraints = [
            models.UniqueConstraint(fields=["record", "url"], name="unique_ref_url")
        ]

    def __str__(self):
        return f"{self.type}: {self.url}"
