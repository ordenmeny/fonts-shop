from django.urls import path, re_path, include
from rest_framework_simplejwt.views import TokenVerifyView

from users.views import (
    CustomTokenObtainPairView,
    CustomTokenBlacklistView,
    RegisterUserAPIView,
    UpdateUserAPIView,
    RefreshTokenView,
)

app_name = "users"

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='login_token_custom'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),
    re_path(r'api/auth/', include('djoser.urls')),
    path("auth/", include("djoser.urls.jwt")),
    path("api/register/", RegisterUserAPIView.as_view()),
    path("api/update/user/", UpdateUserAPIView.as_view()),
    path("api/token/refresh/", RefreshTokenView.as_view()),
]
