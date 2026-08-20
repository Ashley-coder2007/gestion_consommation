from django.db import models
# PAS d'import de Appareil ici


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


class SignalAgrege(models.Model):
    tick_times = models.DateTimeField()
    puissance_total = models.FloatField()

    class Meta:
        db_table = 'signal_agrege'

    def __str__(self):
        return f"{self.tick_times} - {self.puissance_total}W"


class SignatureElectrique(models.Model):
    id_appareil = models.ForeignKey(
        'Appareils.Appareil',   # ← string aussi ici, comme MesureAppareil
        on_delete=models.CASCADE
    )
    puissance_min = models.FloatField()
    puissance_max = models.FloatField()
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'signature_electrique'

    def __str__(self):
        return f"{self.id_appareil} : {self.puissance_min}-{self.puissance_max}W"