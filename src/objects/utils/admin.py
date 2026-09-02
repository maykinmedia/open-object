class EditInlineAdminMixin:
    extra = 0
    show_change_link = True
    show_add_link = True
    template = "admin/edit_inline/tabular_add_and_edit.html"

    def get_readonly_fields(self, request, obj=None):
        return super().get_fields(request, obj)  # type: ignore[attr-defined]

    def has_add_permission(self, request, obj=None):
        return False
