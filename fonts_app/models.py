import uuid
from django.db import models

from django.contrib.auth import get_user_model
from decimal import Decimal

from django.core.validators import MinValueValidator


class Font(models.Model):
    name = models.CharField(max_length=512)
    author = models.CharField(max_length=256, verbose_name="Имя автора", null=True)
    date_release = models.DateField(null=True, blank=True)
    desc = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шрифты"
        verbose_name_plural = "Шрифты"


class FontStyle(models.Model):
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


class FontFace(models.Model):
    font = models.ForeignKey(
        "Font",
        on_delete=models.CASCADE,
        help_text="Например, NT Somic",
    )
    style = models.ForeignKey(
        "FontStyle",
        on_delete=models.CASCADE,
        help_text="Например, Bold",
    )

    def __str__(self):
        return f"{self.font} {self.style}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["font", "style"], name="uniq_font_style"),
        ]
        verbose_name = "Начертание конкретного шрифта"
        verbose_name_plural = "Начертания конкретного шрифта"


class LicenseType(models.TextChoices):
    DESKTOP5 = "desktop5", "Десктоп до 5 компьютеров"
    DESKTOP10 = "desktop10", "Десктоп до 10 компьютеров"
    DESKTOPMORE10 = "desktopmore10", "Десктоп больше 10 компьютеров"

    APP1 = "app1", "1 приложение"
    APP2 = "app2", "2 приложения"
    APP5 = "app5", "5 приложений"
    APPMORE5 = "appmore5", "Больше 5 приложений"


class FontFacePrice(models.Model):
    face = models.ForeignKey("FontFace", on_delete=models.CASCADE)
    license_type = models.CharField(max_length=128, choices=LicenseType.choices)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )
    currency = models.CharField(max_length=16, default="Руб")

    def __str__(self):
        return f"{self.face} на {self.license_type} за {self.price}{self.currency}"

    class Meta:
        verbose_name = "Стоимость лицензии начертания шрифта"
        verbose_name_plural = "Стоимости лицензий начертания шрифта"


class Order(models.Model):
    number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ от {self.created_at} №{self.number} пользователя {self.user}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items")
    # font_face = models.ForeignKey("FontFace", on_delete=models.CASCADE)
    font_face_with_price = models.ForeignKey("FontFacePrice", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Заказ {self.order.number}: {self.font_face_with_price} для пользователя {self.order.user}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "font_face_with_price"], name="uniq_order_fontface"
            )
        ]

        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказов"
