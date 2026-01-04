from django.urls import path
from .views import GetFont, AllFont

urlpatterns = [
    path('all-fonts/', AllFont.as_view(), name="all_fonts"),
    path('get-font/<int:pk_font>/', GetFont.as_view(), name="get_font"),
]