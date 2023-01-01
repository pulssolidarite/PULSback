from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
)

from fleet.models import User, Customer, Campaign


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Informations personelles"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                )
            },
        ),
        (
            _(
                "Permissions d'accès aux différentes fonctions de ce dashboard administrateur (pour les admins seulement)"
            ),
            {
                "fields": (
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "username",
        "is_active",
        "_type",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = (
        "email",
        "username",
    )
    ordering = ("username",)

    def _type(self, obj: User):
        if obj.is_staff:
            return "Admin"
        elif obj.is_terminal_user():
            return "Terminal"
        elif obj.is_customer_user():
            return "Customer"
        else:
            return None

    _type.short_description = _("Type")


admin.site.register(Customer)
admin.site.register(Campaign)
