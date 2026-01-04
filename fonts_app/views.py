from rest_framework.generics import ListAPIView
from .models import FontFacePrice
from .serializers import FontFacePriceSerializer


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
