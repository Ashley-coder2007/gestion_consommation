from rest_framework import generics
from .models import Statistique
from .serializers import StatistiqueSerializer


class StatistiqueListCreateAPIView(generics.ListCreateAPIView):
    queryset = Statistique.objects.all()
    serializer_class = StatistiqueSerializer