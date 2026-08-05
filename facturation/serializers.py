from rest_framework import serializers
from .models import Facture, TarifElectrique

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'

class TarifElectriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarifElectrique
        fields = '__all__'