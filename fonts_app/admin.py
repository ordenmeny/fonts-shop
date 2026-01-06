from django.contrib import admin

from .models import (
    Font,
    FontStyle,
    FontFace,
    FontFacePrice,
    Order,
    OrderItem,
    Cart,
)

admin.site.register(Font)
admin.site.register(FontStyle)
admin.site.register(FontFace)
admin.site.register(FontFacePrice)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
