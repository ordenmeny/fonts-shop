from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from fonts_app.views import csrf


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("api/fonts/", include("fonts_app.urls")),
    path("api/csrf/", csrf),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
