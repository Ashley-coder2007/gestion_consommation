from rest_framework import generics
from .models import TarifElectrique, Facture
from .serializers import TarifElectriqueSerializer, FactureSerializer


class TarifListCreateAPIView(generics.ListCreateAPIView):
    queryset = TarifElectrique.objects.all()
    serializer_class = TarifElectriqueSerializer


class FactureListCreateAPIView(generics.ListCreateAPIView):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer