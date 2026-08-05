from rest_framework import generics
from .models import Consommation
from .serializers import ConsommationSerializer


class ConsommationListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  -> liste des mesures (pour debug ou dashboard externe)
    POST -> l'ESP32 envoie une nouvelle mesure ici
    """
    queryset = Consommation.objects.all()
    serializer_class = ConsommationSerializer