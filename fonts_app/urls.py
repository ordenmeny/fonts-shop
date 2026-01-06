from django.urls import path
from .views import GetFontLicenses, AllLicenses, GetLicensesByStyle, AddToCart, AllFonts

urlpatterns = [
    path("all-fonts/", AllFonts.as_view(), name="all_fonts"),
    path("all-licenses/", AllLicenses.as_view(), name="all_licenses"),
    path("get-license/<int:pk_font>/", GetFontLicenses.as_view(), name="get_license"),
    path(
        "get-licenses-by-face/<int:pk_face>/",
        GetLicensesByStyle.as_view(),
        name="get_styles_and_licenses",
    ),
    path("add-to-cart/<int:pk_item>/", AddToCart.as_view(), name="add_to_cart"),
]
