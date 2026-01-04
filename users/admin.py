from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import (
    Font,
    FontStyle,
    FontFace,
    FontFacePrice,
    Order,
    OrderItem,
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

admin.site.register(Font)
admin.site.register(FontStyle)
admin.site.register(FontFace)
admin.site.register(FontFacePrice)
admin.site.register(Order)
admin.site.register(OrderItem)
