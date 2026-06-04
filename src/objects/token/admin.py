from django.contrib import admin
from django.contrib.admin.utils import unquote

from objects.api.serializers import ObjectSerializer
from objects.core.models import ObjectType
from objects.utils.admin import EditInlineAdminMixin
from objects.utils.serializers import build_spec, get_field_names

from .constants import PermissionModes
from .models import Permission, TokenAuth

EMPTY_FIELD_CHOICE = ("", "---------")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "token_auth",
        "object_type",
        "mode",
        "use_fields",
        "get_uuid",
    )

    @admin.display(description="Object type UUID")
    def get_uuid(self, obj):
        return obj.object_type.uuid

    def get_object_fields(self):
        object_serializer = ObjectSerializer()
        object_fields = build_spec(get_field_names(object_serializer.fields), ui=True)
        return object_fields

    def get_form_data(self, request, object_id) -> dict:
        obj = self.get_object(request, unquote(object_id)) if object_id else None
        ModelForm = self.get_form(request, obj, change=not obj)

        initial = {}
        token_auth_id = request.GET.get("token_auth") or request.GET.get(
            "initial-token_auth"
        )
        if token_auth_id and not obj:
            initial["token_auth"] = token_auth_id

        if request.method == "POST":
            form = ModelForm(request.POST, request.FILES, instance=obj)
        else:
            form = ModelForm(instance=obj, initial=initial)
        form.is_valid()

        values = {field.name: field.value() for field in form}
        if obj and obj.object_type:
            values["object_type"] = str(obj.object_type.uuid)
        errors = (
            {
                field: [
                    {"msg": next(iter(error)), "code": error.code} for error in _errors
                ]
                for field, _errors in form.errors.as_data().items()
            }
            if form.is_bound
            else {}
        )
        return {"values": values, "errors": errors}

    def get_extra_context(self, request, object_id):
        mode_choices = [EMPTY_FIELD_CHOICE] + list(PermissionModes.choices)
        token_auth_choices = [EMPTY_FIELD_CHOICE] + [
            (token.pk, str(token)) for token in TokenAuth.objects.all()
        ]
        object_type_choices = [EMPTY_FIELD_CHOICE] + [
            (str(object_type.uuid), str(object_type))
            for object_type in ObjectType.objects.order_by("name")
        ]
        return {
            "object_fields": self.get_object_fields(),
            "token_auth_choices": token_auth_choices,
            "object_type_choices": object_type_choices,
            "mode_choices": mode_choices,
            "form_data": self.get_form_data(request, object_id),
        }

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_extra_context(request, object_id))

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_extra_context(request, object_id=None))

        return super().add_view(request, form_url, extra_context)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)

        # Although Permission.object_type is stored as a ForeignKey to the PK of ObjectType,
        # the admin form now submits the UUID as the choice value.
        # to_field_name = "uuid" tells Django to resolve the submitted UUID to the correct ObjectType instance.
        # Django then automatically stores its PK internally
        form.base_fields["object_type"].to_field_name = "uuid"

        return form


class PermissionInline(EditInlineAdminMixin, admin.TabularInline):
    model = Permission
    fk_name = "token_auth"
    fields = (
        "object_type",
        "mode",
        "use_fields",
        "fields",
        "get_uuid",
    )

    @admin.display(description="Object type UUID")
    def get_uuid(self, obj):
        return obj.object_type.uuid


@admin.register(TokenAuth)
class TokenAuthAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "contact_person",
        "organization",
        "administration",
        "application",
        "is_superuser",
    )
    readonly_fields = ("token",)
    inlines = [PermissionInline]
