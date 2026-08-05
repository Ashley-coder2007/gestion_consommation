from django.db import models


class Appareil(models.Model):
    class TypeCourant(models.TextChoices):
        CONTINU = 'DC', 'Courant continu'
        ALTERNATIF = 'AC', 'Courant alternatif'

    class Statut(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activé'
        DESACTIVE = 'DESACTIVE', 'Désactivé'

    id_appareil = models.AutoField(
        primary_key=True,
        db_column="id_appareil"
    )
    nom = models.CharField(max_length=100)
    type_courant = models.CharField(max_length=2, choices=TypeCourant.choices)
    puissance_nominale = models.FloatField(help_text="Puissance nominale en Watts")
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.ACTIVE)

    class Meta:
        db_table = 'appareils'
        managed = False
        verbose_name = 'Appareil'
        verbose_name_plural = 'Appareils'

    def __str__(self):
        return self.nom