from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    default_error_messages = {"no_active_account": "Неверный email или пароль"}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return password

    def create(self, validated_data):
        validated_data["username"] = validated_data["email"]
        password = validated_data.pop("password")

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        return instance


class HobbyUpdateSerializer(serializers.Serializer):
    hobby = serializers.ListField(child=serializers.IntegerField(), required=True)
