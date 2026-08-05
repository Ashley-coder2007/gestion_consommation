from rest_framework import serializers
from .models import Statistique

class StatistiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistique
        fields = '__all__'