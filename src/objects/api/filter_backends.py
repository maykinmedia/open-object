from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from objects.utils.serializers import get_field_names_and_sources


class OrderingBackend(OrderingFilter):
    """
    This backend can be used when DB fields have different names/paths than
    serializer fields. It keeps the mapping between the serializer and DB fields and
    also supports ordering on nested fields.

    It also supports ordering on any attribute of JSON field.
    """

    json_field = None
    ordering_description = _(  # pyright: ignore[reportAssignmentType]
        "Comma-separated fields, which are used to order results. "
        "For descending order use '-' as prefix. Nested fields are also supported. "
        "For example: '-record__data__length,record__index'."
    )

    def get_valid_fields(self, queryset, view, context=None):
        """add nested fields to available fields for ordering"""
        if context is None:
            context = {}
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)

        if valid_fields is None:
            # Default to allowing filtering on serializer fields
            return self.get_default_valid_fields(queryset, view, context)

        elif valid_fields == "__all__":
            # View explicitly allows filtering on any model field
            serializer = view.get_serializer()  # pyright: ignore[reportAttributeAccessIssue]
            all_serializer_fields = get_field_names_and_sources(serializer.fields)
            valid_fields = [
                (name, source)
                for name, source in all_serializer_fields
                if source != "*"
            ]
        else:
            valid_fields = [
                (item, item) if isinstance(item, str) else item for item in valid_fields
            ]

        return valid_fields

    def remove_invalid_fields(self, queryset, fields, view, request):
        """add support for JSON fields and validation check for allowed fields"""
        valid_fields = [
            item[0]
            for item in self.get_valid_fields(queryset, view, {"request": request})
        ]
        json_field = self.get_json_field(view)

        def term_valid(term):
            term = term.removeprefix("-")

            return term in valid_fields or (
                json_field and term.startswith(f"{json_field}__")
            )

        ordering = [term for term in fields if term_valid(term)]

        # check that all fields are allowed
        permissions = request.auth.permissions.filter(use_fields=True)  # pyright: ignore[reportAttributeAccessIssue]
        allowed_fields = sum([list(p.fields.values()) for p in permissions], [])

        def term_allowed(term):
            term = term.removeprefix("-")
            # support ` level of nested fields
            return all([term in allowed for allowed in allowed_fields]) or (
                "__" in term
                and all(
                    [
                        term.rsplit("__", maxsplit=1)[0] in allowed
                        for allowed in allowed_fields
                    ]
                )
            )

        not_allowed = [term for term in ordering if not term_allowed(term)]
        if not_allowed:
            raise ValidationError(
                _("You are not allowed to sort on following fields: %s")
                % ", ".join(not_allowed)
            )

        return ordering

    def filter_queryset(self, request, queryset, view):
        # convert serializer fields to DB model ones
        db_ordering = self.get_db_ordering(request, queryset, view)

        if db_ordering:
            return queryset.order_by(*db_ordering)

        return queryset

    def get_json_field(self, view):
        return getattr(view, "json_field", self.json_field)

    def get_db_ordering(self, request, queryset, view) -> list:
        """get serializer ordering fields and convert them to db fields"""
        ordering = self.get_ordering(request, queryset, view)
        ordering = ordering or []

        valid_fields = dict(self.get_valid_fields(queryset, view, {"request": request}))
        json_field = self.get_json_field(view)

        db_ordering = []
        for order_field in ordering:
            prefix = "-" if order_field.startswith("-") else ""
            base = order_field if not order_field.startswith("-") else order_field[1:]

            if base in valid_fields:
                db_ordering.append(f"{prefix}{valid_fields[base]}")
            # json nested attribute
            elif (
                json_field
                and base.startswith(f"{json_field}__")
                and json_field in valid_fields
            ):
                nested_property = base[len(f"{json_field}") :]
                db_ordering.append(
                    f"{prefix}{valid_fields[json_field]}{nested_property}"
                )

        return db_ordering
