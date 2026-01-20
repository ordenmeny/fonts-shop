import uuid
import pandas as pd
from rest_framework.permissions import IsAdminUser

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FontFacePrice, Cart, Font, Order, OrderItem, LicenseType
from .serializers import (
    FontFacePriceSerializer,
    FontSerializer,
    CartSerializer,
    OrderSerializer,
)

from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .service import CartService


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})


class AllFontsView(ListAPIView):
    model = Font
    serializer_class = FontSerializer
    queryset = Font.objects.all()


class GetFontLicensesView(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer

    def get_queryset(self):
        pk_font = self.kwargs["pk_font"]
        return FontFacePrice.objects.select_related(
            "face__font",
            "face__style",
        ).filter(face__font__pk=pk_font)


class AllLicensesView(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer
    queryset = FontFacePrice.objects.select_related(
        "face__font",
        "face__style",
    ).all()


class GetLicensesByStyleView(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer

    def get_queryset(self):
        pk_face = self.kwargs["pk_face"]
        return FontFacePrice.objects.select_related(
            "face__font",
            "face__style",
        ).filter(face__pk=pk_face)


class RemoveFromCartView(APIView):
    model = Cart
    serializer_class = CartSerializer

    def delete(self, request, pk_item):
        user = request.user
        cart_id_from_cookies = request.COOKIES.get("cart_id")

        cart = None
        if user.is_authenticated:
            cart = self.model.objects.filter(user=user).first()

        if cart_id_from_cookies and cart is None:
            cart = self.model.objects.filter(pk=cart_id_from_cookies).first()

        cart.items.remove(pk_item)
        cart.save()

        data = self.serializer_class(cart)

        return Response(data.data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
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


class CartView(APIView):
    model = Cart
    serializer_class = CartSerializer

    def get(self, request):
        cart = CartService.get_cart_object(request)

        data = self.serializer_class(cart)

        return Response(data.data, status=status.HTTP_200_OK)


class CreateOrderView(APIView):
    def post(self, request):
        cart = CartService.get_cart_object(request)

        if cart is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=cart.user,
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                font_face_with_price=item,
            )

        Cart.objects.filter(user=cart.user).delete()

        return Response(status=status.HTTP_200_OK)


class UserOrdersView(ListAPIView):
    model = Order
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class UserOrdersAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        qs = (
            OrderItem.objects.select_related(
                "order",
                "font_face_with_price__face__font",
                "font_face_with_price__face__style",
            )
            .filter(order__user=request.user, font_face_with_price__isnull=False)
            .values(
                "order__created_at",
                "font_face_with_price__license_type",
                "font_face_with_price__price",
                "font_face_with_price__face__font__name",
                "font_face_with_price__face__style__name",
            )
        )

        df = pd.DataFrame.from_records(qs)
        if df.empty:
            return Response(
                {
                    "total_items": 0,
                    "by_font": {},
                    "by_license": {},
                    "by_style": {},
                    "revenue_total": 0,
                },
                status=status.HTTP_200_OK,
            )

        license_map = dict(LicenseType.choices)
        df["license_type_label"] = df["font_face_with_price__license_type"].map(
            license_map
        )

        df["price"] = df["font_face_with_price__price"].astype(float)
        df["font_name"] = df["font_face_with_price__face__font__name"].astype(str)
        df["style_name"] = df["font_face_with_price__face__style__name"].astype(str)

        by_font = df.groupby("font_name").size().sort_values(ascending=False).to_dict()
        by_license = (
            df.groupby("license_type_label")
            .size()
            .sort_values(ascending=False)
            .to_dict()
        )
        by_style = (
            df.groupby("style_name").size().sort_values(ascending=False).to_dict()
        )

        revenue_total = round(float(df["price"].sum()), 2)

        return Response(
            {
                "total_items": int(len(df)),
                "by_font": by_font,
                "by_license": by_license,
                "by_style": by_style,
                "revenue_total": revenue_total,
            },
            status=status.HTTP_200_OK,
        )
