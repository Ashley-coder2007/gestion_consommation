from rest_framework import serializers
from .models import TarifElectrique, Facture


class TarifElectriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarifElectrique
        fields = ["id", "prix_kwh", "date_debut_validite", "date_fin_validite"]


class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = ["id", "appareil", "periode_debut", "periode_fin", "cout_total", "date_generation"]