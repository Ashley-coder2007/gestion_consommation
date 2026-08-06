from rest_framework import serializers
from .models import Appareil


class AppareilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appareil
        fields = [
            "id_appareil", "nom", "type_courant", "puissance_nominale",
            "statut", "categorie", "heures_par_jour",
        ]