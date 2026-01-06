import uuid

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FontFacePrice, Cart, Font
from .serializers import FontFacePriceSerializer, FontSerializer

from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})


class AllFonts(ListAPIView):
    model = Font
    serializer_class = FontSerializer
    queryset = Font.objects.all()


class GetFontLicenses(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer

    def get_queryset(self):
        pk_font = self.kwargs["pk_font"]
        return FontFacePrice.objects.select_related(
            "face__font",
            "face__style",
        ).filter(face__font__pk=pk_font)


class AllLicenses(ListAPIView):
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
            if FontFacePrice.objects.get(pk=pk_item) not in cart.items.all():
                cart.sum += FontFacePrice.objects.get(pk=pk_item).price

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

        if FontFacePrice.objects.get(pk=pk_item) not in cart.items.all():
            cart.sum += FontFacePrice.objects.get(pk=pk_item).price

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
