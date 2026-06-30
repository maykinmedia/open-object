from __future__ import annotations

import io
import json
from functools import partial
from typing import Sequence

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.gis.db.models import GeometryField
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import structlog
from jsonsuit.widgets import READONLY_WIDGET_MEDIA_CSS, READONLY_WIDGET_MEDIA_JS
from vng_api_common.utils import get_help_text

from objects.api.v2.filters import filter_queryset_by_data_attr

from .constants import ObjectTypeVersionStatus
from .forms import FileImportForm, ObjectTypeVersionForm, UrlImportForm
from .import_export import export_data, import_upload
from .models import Object, ObjectRecord, ObjectType, ObjectTypeVersion
from .widgets import JSONSuit

logger = structlog.stdlib.get_logger(__name__)


def can_change(obj) -> bool:
    if not obj:
        return True

    if not obj.last_version:
        return True

    if obj.last_version.status == ObjectTypeVersionStatus.draft:
        return True

    return False


class ObjectTypeVersionInline(admin.StackedInline):
    verbose_name_plural = _("last version")
    model = ObjectTypeVersion
    form = ObjectTypeVersionForm
    extra = 0
    max_num = 1
    min_num = 1
    readonly_fields = ("version", "status", "published_at")
    formfield_overrides = {
        models.JSONField: {
            "widget": JSONSuit,
            "error_messages": {
                "invalid": _("'%(value)s' value must be valid JSON"),
            },
        }
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = request.resolver_match.kwargs.get("object_id")
        if not parent_id:
            return queryset

        last_version = (
            queryset.filter(object_type_id=parent_id).order_by("-version").first()
        )
        if not last_version:
            return queryset.none()
        return queryset.filter(id=last_version.id)

    def has_delete_permission(self, request, obj=None):
        return False

    # work around to prettify readonly JSON field
    def get_exclude(self, request, obj=None):
        if not can_change(obj):
            return ("json_schema",)
        return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not can_change(obj):
            local_fields = [field.name for field in self.opts.local_fields]
            # work around to prettify readonly JSON field
            local_fields.remove("json_schema")
            local_fields.append("json_schema_readonly")
            return local_fields

        return super().get_readonly_fields(request, obj)

    def json_schema_readonly(self, obj):
        return format_html(
            '<div class="suit"><pre><code class="language-json">{}</code></pre></div>',
            json.dumps(obj.json_schema, indent=2),
        )

    json_schema_readonly.short_description = "JSON schema"

    class Media:
        js = READONLY_WIDGET_MEDIA_JS
        css = READONLY_WIDGET_MEDIA_CSS


@admin.register(ObjectType)
class ObjectTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_plural",
        "allow_geometry",
        "has_format_checker_display",
    )
    search_fields = ("name", "name_plural", "uuid")
    inlines = [ObjectTypeVersionInline]

    change_list_template = "admin/core/objecttype/object_list.html"

    actions = ["export_objecttypes_action"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-from-url/",
                self.admin_site.admin_view(self.import_from_url_view),
                name="import_from_url",
            ),
            path(
                "import-from-file/",
                self.admin_site.admin_view(self.import_from_file_view),
                name="import_from_file",
            ),
        ]
        return my_urls + urls

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj:
            readonly_fields = ("uuid",) + readonly_fields

        return readonly_fields

    def has_format_checker_display(self, obj):
        return obj.has_format_checker

    has_format_checker_display.boolean = True
    has_format_checker_display.short_description = "Format Checker Enabled"

    def publish(self, request, obj):
        last_version = obj.last_version
        last_version.status = ObjectTypeVersionStatus.published
        last_version.save()

        msg = format_html(
            _("The object type {version} has been published successfully!"),
            version=obj.last_version,
        )
        self.message_user(request, msg, level=messages.SUCCESS)

        return HttpResponseRedirect(request.path)

    def add_new_version(self, request, obj: ObjectType):
        new_version = obj.last_version
        assert new_version
        new_version.pk = None
        new_version.version = None
        new_version.status = ObjectTypeVersionStatus.draft
        new_version.save()

        msg = format_html(
            _("The new version {version} has been created successfully!"),
            version=new_version,
        )
        self.message_user(request, msg, level=messages.SUCCESS)

        return HttpResponseRedirect(request.path)

    def response_change(self, request, obj):
        if "_publish" in request.POST:
            return self.publish(request, obj)

        if "_newversion" in request.POST:
            return self.add_new_version(request, obj)

        return super().response_change(request, obj)

    def import_from_url_view(self, request):
        if request.method == "POST":
            form = UrlImportForm(request.POST)
            if form.is_valid():
                form_json = form.cleaned_data.get("json")

                ObjectType.objects.create_from_schema(
                    json_schema=form_json,
                    name_plural=form.data.get("name_plural", "").title(),
                )
                return redirect(reverse("admin:core_objecttype_changelist"))
        else:
            form = UrlImportForm()

        return render(
            request, "admin/core/objecttype/object_import_form.html", {"form": form}
        )

    def import_from_file_view(self, request: HttpRequest) -> HttpResponse:
        if request.method == "POST":
            form = FileImportForm(request.POST, files=request.FILES)
            if form.is_valid():
                imported_types = import_upload(
                    form.files["export_file"],
                    form.cleaned_data["keep_uuid"],
                    partial(form.add_error, "export_file"),
                )
                if not form.errors and not imported_types:
                    form.add_error(
                        "export_file", _("Found nothing importable in that file")
                    )
                if not form.errors:
                    self.message_user(
                        request,
                        _("{resource_types} imported successfully.").format(
                            resource_types=",".join(imported_types)
                        ),
                    )
                    return redirect(reverse("admin:core_objecttype_changelist"))
        else:
            form = FileImportForm()

        return render(
            request,
            "admin/core/objecttype/object_import_form.html",
            {"form": form, "source": "file"},
        )

    @admin.action(description=_("Export selected objecttypes as a file"))
    def export_objecttypes_action(
        self, request: HttpRequest, queryset: models.QuerySet[ObjectType]
    ) -> HttpResponse:
        output = io.BytesIO()
        export_data(output, objecttypes=queryset)

        response = HttpResponse(output.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = (
            'attachment; filename="objecttypes-export.zip"'
        )
        return response


class ObjectRecordForm(forms.ModelForm):
    class Meta:
        model = ObjectRecord
        help_texts = {
            "geometry": get_help_text("core.ObjectRecord", "geometry")
            + "\n\n format: SRID=4326;POINT|LINESTRING|POLYGON (LAT LONG, ...)"
        }
        fields = "__all__"


class ObjectRecordInline(admin.TabularInline):
    form = ObjectRecordForm
    model = ObjectRecord
    extra = 1
    readonly_fields = (
        "index",
        "registration_at",
        "end_at",
        "get_corrected_by",
        "created_on",
        "modified_on",
    )
    fields = (
        "index",
        "version",
        "data",
        "geometry",
        "start_at",
        "end_at",
        "registration_at",
        "get_corrected_by",
        "correct",
        "created_on",
        "modified_on",
    )

    formfield_overrides = {GeometryField: {"widget": forms.Textarea}}

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "correct":
            object_id = request.resolver_match.kwargs.get("object_id")
            if not object_id:
                kwargs["queryset"] = ObjectRecord.objects.none()
            else:
                kwargs["queryset"] = ObjectRecord.objects.filter(
                    object_id=int(object_id), corrected__isnull=True
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_corrected_by(self, obj):
        return obj.corrected

    get_corrected_by.short_description = "corrected by"


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_type",
        "current_record",
        "uuid",
        "get_object_type_uuid",
        "modified_on",
        "created_on",
    )
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
    list_filter = ("object_type", "created_on", "modified_on")

    def get_search_fields(self, request: HttpRequest) -> Sequence[str]:
        if settings.OBJECTS_ADMIN_SEARCH_DISABLED:
            return ()

        return ("uuid",)

    change_list_template = "admin/core/object_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["toggle_show"] = _("Show search instructions")
        extra_context["toggle_hide"] = _("Hide search instructions")
        extra_context["search_enabled"] = bool(self.get_search_fields(request))
        return super().changelist_view(request, extra_context=extra_context)

    def get_search_results(self, request, queryset, search_term):
        VALID_OPERATORS = {"exact", "icontains", "in", "gt", "gte", "lt", "lte"}
        DEFAULT_OPERATOR = "icontains"

        if settings.OBJECTS_ADMIN_SEARCH_DISABLED:
            return queryset, False

        if "__" not in search_term:
            return super().get_search_results(request, queryset, search_term)

        parts = search_term.rsplit("__", 2)

        if len(parts) == 3 and parts[1] in VALID_OPERATORS:
            key, operator, str_value = parts
        elif len(parts) == 3:
            key = "__".join(parts[:-1])
            operator = DEFAULT_OPERATOR
            str_value = parts[-1]
        elif len(parts) == 2:
            key, str_value = parts
            operator = DEFAULT_OPERATOR
        else:
            return super().get_search_results(request, queryset, search_term)

        if not key or not str_value:
            return super().get_search_results(request, queryset, search_term)

        queryset = filter_queryset_by_data_attr(
            queryset,
            key.strip(),
            operator,
            str_value.strip(),
            field_prefix="records__data",
        )
        return queryset.distinct(), False

    @admin.display(description="Object type UUID")
    def get_object_type_uuid(self, obj):
        return obj.object_type.uuid

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj:
            readonly_fields = (
                "uuid",
                "get_object_type_uuid",
                "object_type",
                "created_on",
                "modified_on",
            ) + readonly_fields

        return readonly_fields
