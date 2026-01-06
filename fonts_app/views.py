import uuid

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FontFacePrice, Cart
from .serializers import FontFacePriceSerializer

from django.conf import settings


class GetFont(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer

    def get_queryset(self):
        pk_font = self.kwargs["pk_font"]
        return FontFacePrice.objects.select_related(
            "face__font",
            "face__style",
        ).filter(face__font__pk=pk_font)


class AllFont(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer
    queryset = FontFacePrice.objects.select_related(
        "face__font",
        "face__style",
    ).all()


class GetLicensesByStyle(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer

    def get_queryset(self):
        pk_face = self.kwargs["pk_face"]
        return FontFacePrice.objects.select_related(
            "face__font",
            "face__style",
        ).filter(face__style__pk=pk_face)


class AddToCart(APIView):
    model = Cart

    def post(self, request, pk_item):
        cart_id_from_cookies = request.COOKIES.get("cart_id")
        user = request.user
        response = Response(status=status.HTTP_200_OK)

        if user.is_authenticated and cart_id_from_cookies:
            cart = self.model.objects.filter(pk=cart_id_from_cookies).first()
            cart.user = user
            cart.save()

        cart = None
        if user.is_authenticated:
            cart = self.model.objects.filter(user=user).first()
        elif cart_id_from_cookies:
            cart = self.model.objects.filter(pk=cart_id_from_cookies).first()

        if cart:
            cart.items.add(pk_item)
            cart.save()
            return response

        if user.is_authenticated:
            cart = self.model.objects.create(
                pk=uuid.uuid4(),
                user=user,
            )
        else:
            cart = self.model.objects.create(pk=uuid.uuid4())

        cart.items.add(pk_item)
        cart.save()

        response.set_cookie(
            key="cart_id",
            value=cart.pk,
            httponly=True,
            secure=True if settings.DEBUG else False,
            samesite="Lax",
        )

        return response
