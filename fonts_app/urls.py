from django.urls import path
from .views import (
    GetFontLicensesView,
    AllLicensesView,
    GetLicensesByStyleView,
    AddToCartView,
    AllFontsView,
    CartView,
)

urlpatterns = [
    path("all-fonts/", AllFontsView.as_view(), name="all_fonts"),
    path("all-licenses/", AllLicensesView.as_view(), name="all_licenses"),
    path("get-license/<int:pk_font>/", GetFontLicensesView.as_view(), name="get_license"),
    path(
        "get-licenses-by-face/<int:pk_face>/",
        GetLicensesByStyleView.as_view(),
        name="get_styles_and_licenses",
    ),
    path("add-to-cart/<int:pk_item>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/", CartView.as_view(), name='cart'),
]
