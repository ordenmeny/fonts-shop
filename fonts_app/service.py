from .models import Cart

class CartService:
    model = Cart

    @classmethod
    def get_cart_object(cls, request):
        user = request.user
        cart_id_from_cookies = request.COOKIES.get("cart_id")
        cart = None
        if user.is_authenticated:
            cart = cls.model.objects.filter(user=user).first()

        if cart_id_from_cookies and cart is None:
            cart = cls.model.objects.filter(pk=cart_id_from_cookies).first()

        return cart