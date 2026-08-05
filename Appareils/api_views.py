from rest_framework import generics
from .models import Appareil
from .serializers import AppareilSerializer


class AppareilListCreateAPIView(generics.ListCreateAPIView):
    queryset = Appareil.objects.all()
    serializer_class = AppareilSerializer


class AppareilDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appareil.objects.all()
    serializer_class = AppareilSerializer
    lookup_field = "pk"