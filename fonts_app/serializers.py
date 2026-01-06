from rest_framework import serializers
from .models import FontFacePrice, Font, Cart


class FontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font
        fields = "__all__"


class FontFacePriceSerializer(serializers.ModelSerializer):
    font_name = serializers.CharField(source="face.font.name", read_only=True)
    font_author = serializers.CharField(source="face.font.author", read_only=True)
    font_date_release = serializers.CharField(
        source="face.font.date_release", read_only=True
    )
    font_desc = serializers.CharField(source="face.font.desc", read_only=True)

    style_name = serializers.CharField(source="face.style.name", read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["license_type_label"] = instance.get_license_type_display()
        return data

    class Meta:
        model = FontFacePrice
        fields = "__all__"


class StylesAndLicensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FontFacePrice
        fields = "__all__"


class CartSerializer(serializers.Serializer):
    items = FontFacePriceSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"