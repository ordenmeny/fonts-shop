from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import (
    Fonts,
    FontStyles,
    FontStylePrices,
    FontOrders,
    UserOrders,
)


class CustomUserAdmin(UserAdmin):
    list_display = (
        "first_name",
        "last_name",
        "username",
        "email",
        "date_joined",
    )
    list_display_links = ("first_name", "last_name", "username", "email")

    fields_to_set = (
        "email",
        "first_name",
        "last_name",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": fields_to_set}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(get_user_model(), CustomUserAdmin)

admin.site.register(Fonts)
admin.site.register(FontStyles)
admin.site.register(FontStylePrices)
admin.site.register(FontOrders)
admin.site.register(UserOrders)

