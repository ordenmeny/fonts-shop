from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import FontFacePrice
from .serializers import FontFacePriceSerializer

class GetFont(APIView):
    def get(self, request, pk_font):
        model = FontFacePrice.objects.filter(face__font__pk=pk_font)
        serializer = FontFacePriceSerializer(model, many=True)
        return Response(serializer.data)


class AllFont(ListAPIView):
    model = FontFacePrice
    serializer_class = FontFacePriceSerializer
    queryset = FontFacePrice.objects.all()
