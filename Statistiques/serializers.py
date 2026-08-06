from rest_framework import serializers
from .models import Statistique


class StatistiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistique
        fields = [
            "id", "appareil", "periodicite", "date_reference",
            "consommation_moyenne", "consommation_max", "consommation_min",
        ]