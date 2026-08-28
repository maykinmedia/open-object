from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_filters import fields as filter_fields, filters
from vng_api_common.filters import URLModelChoiceFilter


class ObjectTypeField(filter_fields.ModelChoiceField):
    default_error_messages = {
        "max_length": _("The value has too many characters"),
        "min_length": _("The value has too few characters"),
        "invalid_choice": _(
            "Select a valid object type. %(value)s is not one of the available choices."
        ),
        "invalid": _("Invalid value."),
    }

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop("max_length", None)
        self.min_length = kwargs.pop("min_length", None)

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(self.error_messages["max_length"], code="max_length")

        if self.min_length and len(value) < self.min_length:
            raise ValidationError(self.error_messages["min_length"], code="min_length")

        assert self.queryset is not None

        try:
            result = self.queryset.get_by_url(value)  # type: ignore[reportAttributeAccessIssue]
        except self.queryset.model.DoesNotExist:
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        return result


class ObjectTypeFilter(URLModelChoiceFilter):
    field_class = ObjectTypeField


class ManyWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        if name not in data:
            return []

        return data.getlist(name)  # type: ignore[reportIncompatibleMethodOverride]


class ManyCharField(forms.CharField):
    widget = ManyWidget

    def to_python(self, value):  # type: ignore[reportIncompatibleMethodOverride]
        if not value:
            return []

        return value


class ManyCharFilter(filters.CharFilter):
    # django-filter doesn't support several uses of the same query param out of the box
    # so we need to do it ourselves
    field_class = ManyCharField
