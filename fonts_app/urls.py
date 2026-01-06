from django.urls import path
from .views import GetFont, AllFont, GetLicensesByStyle, AddToCart

urlpatterns = [
    path("all-licenses/", AllFont.as_view(), name="all_fonts"),
    path("get-license/<int:pk_font>/", GetFont.as_view(), name="get_font"),
    path(
        "get-licenses-by-face/<int:pk_face>/",
        GetLicensesByStyle.as_view(),
        name="get_styles_and_licenses",
    ),
    path("add-to-cart/<int:pk_item>/", AddToCart.as_view(), name="add_to_cart")
]
