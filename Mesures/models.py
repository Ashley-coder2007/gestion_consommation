
from django.db import models


class Mesure(models.Model):
    id_mesure = models.BigAutoField(primary_key=True, db_column='id_mesure')
    date_heure = models.DateTimeField()
    puissance_active = models.FloatField(null=True, blank=True, help_text="Watts")
    courant = models.FloatField(null=True, blank=True, help_text="Ampères")
    tension = models.FloatField(null=True, blank=True, help_text="Volts")
    facteur_puissance = models.FloatField(null=True, blank=True)
    energie = models.FloatField(null=True, blank=True, help_text="kWh")
    frequence = models.FloatField(null=True, blank=True, help_text="Hz")

    class Meta:
        db_table = 'mesures'
        managed = False
        verbose_name = 'Mesure'
        verbose_name_plural = 'Mesures'
        ordering = ['date_heure']

    def __str__(self):
        return f"Mesure du {self.date_heure}"


class MesureAppareil(models.Model):
    id_mesures_appareils = models.AutoField(primary_key=True, db_column='id_mesures_appareils')
    mesure = models.ForeignKey(
        Mesure,
        on_delete=models.CASCADE,
        db_column='id_mesure',
        related_name='mesures_appareils'
    )
    appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        db_column='id_appareil',
        related_name='mesures_appareils'
    )

    class Meta:
        db_table = 'mesures_appareils'
        managed = False
        verbose_name = 'Association Mesure-Appareil'
        verbose_name_plural = 'Associations Mesure-Appareil'

    def __str__(self):
        return f"{self.mesure_id} - {self.appareil_id}"
