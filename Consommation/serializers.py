from rest_framework import serializers
from .models import Consommation


class ConsommationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consommation
        fields = ["id", "appareil", "date", "energie_consommee"]