import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenBlacklistSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import (
    RefreshToken
)
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
)
from rest_framework import status
from djoser.email import PasswordResetEmail
from .serializers import (
    EmailTokenObtainPairSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class CustomPasswordResetEmail(PasswordResetEmail):
    template_name = "users/custom_password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["domain"] = "unimatch.ru"
        context["site_name"] = "unimatch.ru"
        context["protocol"] = "https"
        return context


class CustomTokenBlacklistView(TokenBlacklistView):
    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        cookies_refresh_token = request.COOKIES.get('refresh_token')

        serializer = self.get_serializer(data={"refresh": cookies_refresh_token})

        if serializer.is_valid():
            response = Response(
                {
                    "signout": "Вы вышли из системы"
                }, status=status.HTTP_200_OK
            )

            response.delete_cookie(
                key="refresh_token",
                path="/",
                samesite="Lax"
            )

            return response

        return Response({
            "error": "Не получилось выйти из системы"
        }, status=status.HTTP_400_BAD_REQUEST)


class UserByUniqCodeAPIView(RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    lookup_field = "uniq_code"
    lookup_url_kwarg = "uniq_code"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        token, created = Token.objects.get_or_create(user=instance)

        serializer = self.get_serializer(instance)

        return Response({"user": serializer.data, "token": token.key})


class RegisterUserAPIView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            for field, messages in serializer.errors.items():
                if field == "email":
                    for message in messages:
                        if message.code == "unique":
                            return Response({
                                "error": "Пользователь с таким email уже существует"
                            }, status=status.HTTP_400_BAD_REQUEST)
                        if message.code == "invalid":
                            return Response({
                                "error": "Введите правильный адрес электронной почты"
                            }, status=status.HTTP_400_BAD_REQUEST)
                if field == "password":
                    return Response({
                        "error": "Пароль либо слишком простой, либо содержит меньше 4 символов"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if field == "birth":
                    return Response({
                        "error": "Проблема с полем ввода даты рождения"
                    }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    "error": "Произошла непредвиденная ошибка"
                }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        access = refresh_token.access_token

        response = Response(
            {
                "user": UserSerializer(user).data,
                "access": str(access)
            },
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=settings.SECURE_HTTP_ONLY,
            samesite="Lax",
            max_age=24 * 60 * 60,
        )

        return response


class UpdateUserAPIView(UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return Response(
                {"error": "Неверный email или пароль"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        access_token = validated_data.get("access")
        refresh_token = validated_data.pop("refresh")
        response = Response({"access": access_token}, status=status.HTTP_200_OK)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.SECURE_HTTP_ONLY,
            samesite="Lax",
            max_age=24 * 60 * 60,
        )

        return response


class RefreshTokenView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        logger.warning(f"Refresh_token: {refresh_token}")

        if refresh_token is None:
            logger.warning("Необходимо пройти авторизацию")
            return Response(
                {
                    "error": "Необходимо пройти авторизацию",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            logger.warning("Необходимо пройти авторизацию 2")
            return Response(
                {
                    "error": "Необходимо пройти авторизацию",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access = serializer.validated_data.get("access")
        new_refresh = serializer.validated_data.get("refresh")

        logger.warning(f"Access: {access}")
        logger.warning(f"New refresh: {new_refresh}")
        response = Response({"access": access}, status=status.HTTP_200_OK)
        if new_refresh:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh,
                httponly=True,
                secure=settings.SECURE_HTTP_ONLY,
                samesite="Lax",
                max_age=24 * 60 * 60,
            )

        return response
