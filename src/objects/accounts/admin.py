from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from maykin_common.accounts.admin import PreventPrivilegeEscalationMixin

from .models import User


@admin.register(User)
class UserAdmin(PreventPrivilegeEscalationMixin, DjangoUserAdmin):
    pass
