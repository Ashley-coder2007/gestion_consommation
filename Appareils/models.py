from django.db import models


class Appareil(models.Model):
    nom = models.CharField(max_length=100)
    puissance_nominale = models.FloatField()

    class Meta:
        db_table = "appareil"
        managed = False