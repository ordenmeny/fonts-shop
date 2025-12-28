from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


#       order_id     |       product_id
#   №1 (test_user)   |       №10 (NT Somic)


class Fonts(models.Model):
    name = models.CharField(max_length=512)
    author = models.CharField(max_length=256, verbose_name="Имя автора", null=True)
    date_release = models.DateField(auto_now_add=True)
    desc = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шрифты"
        verbose_name_plural = "Шрифты"


class FontStyles(models.Model):
    name = models.CharField(
        max_length=512,
        verbose_name="Название начертания",
        help_text="Например, Extra Bold",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Начертания"
        verbose_name_plural = "Начертания"


class FontStylePrices(models.Model):
    font = models.ForeignKey(
        "Fonts",
        on_delete=models.CASCADE,
        help_text="Например, NT Somic",
    )
    style = models.ForeignKey(
        "FontStyles",
        on_delete=models.CASCADE,
        help_text="Например, Bold",
    )

    # Для конкретного начертация и шрифта
    price_for_5_comp = models.IntegerField()
    price_for_10_comp = models.IntegerField()
    price_for_20_comp = models.IntegerField()

    price_for_10_web_views = models.IntegerField()
    price_for_25_web_views = models.IntegerField()
    price_for_100_web_views = models.IntegerField()

    price_for_1_app = models.IntegerField()
    price_for_2_app = models.IntegerField()
    price_for_5_app = models.IntegerField()

    def __str__(self):
        return f'{self.style} ({self.font})'

    class Meta:
        verbose_name = "Цены начертания шрифта"
        verbose_name_plural = "Цены начертания шрифта"


class FontOrders(models.Model):
    id_order = models.CharField(default="AF-123")

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
    )
    font = models.ForeignKey(
        "Fonts",
        on_delete=models.SET_NULL,
        help_text="Например, NT Somic",
        null=True,
    )
    style = models.ForeignKey(
        "FontStyles",
        on_delete=models.CASCADE,
        help_text="Например, Bold",
    )
    price = models.ForeignKey(
        "FontStylePrices",
        on_delete=models.SET_NULL,
        null=True,
    )  # OneToOneField?

    fields = ...

    def __str__(self):
        return f'Покупка {self.font} {self.style}'

    class Meta:
        verbose_name = "Все заказы"
        verbose_name_plural = "Все заказы"


class UserOrders(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
    )

    fonts = models.ManyToManyField("FontOrders")

    def __str__(self):
        return f'Заказ пользователя {self.user}'

    class Meta:
        verbose_name = "Заказы пользователей"
        verbose_name_plural = "Заказы пользователей"

