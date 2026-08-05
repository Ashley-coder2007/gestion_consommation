from rest_framework import serializers
from .models import Mesure, MesureAppareil

class MesureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesure
        fields = '__all__'

class MesureAppareilSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesureAppareil
        fields = '__all__'