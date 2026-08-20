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


class MesureFine(models.Model):
    """
    Mesures fines à 0.5s (schéma public), utilisées uniquement pour
    construire signature_electrique. Table créée manuellement en base.
    """
    id_mesure_fine = models.BigAutoField(primary_key=True, db_column='id_mesure_fine')
    id_appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        db_column='id_appareil',
        related_name='mesures_fines'
    )
    tick_time = models.DateTimeField(db_column='tick_time')
    puissance_active = models.FloatField(null=True, blank=True, help_text="Watts")
    courant = models.FloatField(null=True, blank=True, help_text="Ampères")
    tension = models.FloatField(null=True, blank=True, help_text="Volts")
    facteur_puissance = models.FloatField(null=True, blank=True)
    energie = models.FloatField(null=True, blank=True, help_text="kWh")
    frequence = models.FloatField(null=True, blank=True, help_text="Hz")

    class Meta:
        # À CONFIRMER : le suffixe "_jan2010" est-il fixe ou temporaire (données de test) ?
        db_table = 'mesures_fines_jan2010'
        managed = False
        verbose_name = 'Mesure fine'
        verbose_name_plural = 'Mesures fines'
        ordering = ['tick_time']

    def __str__(self):
        return f"Mesure fine {self.tick_time} - appareil {self.id_appareil_id}"


class SignalAgrege(models.Model):
    """Schéma agrege — table signal_agrege_jan2010"""
    tick_time = models.DateTimeField(db_column='tick_time')
    puissance_totale_w = models.FloatField(db_column='puissance_totale_w')

    class Meta:
        # À CONFIRMER : même remarque sur le suffixe "_jan2010"
        db_table = '"agrege"."signal_agrege_jan2010"'
        managed = False

    def __str__(self):
        return f"{self.tick_time} - {self.puissance_totale_w}W"


class EstimationNilm(models.Model):
    """
    Schéma agrege — table estimations_nilm_jan2010_py
    Stocke l'historique des résultats du NILM (appareil détecté + puissance estimée).
    """
    tick_time = models.DateTimeField(db_column='tick_time')
    id_appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        db_column='id_appareil',
        related_name='estimations_nilm'
    )
    puissance_estimee = models.FloatField(db_column='puissance_estimee')

    class Meta:
        db_table = '"agrege"."estimations_nilm_jan2010_py"'
        managed = False

    def __str__(self):
        return f"{self.tick_time} - {self.id_appareil_id} : {self.puissance_estimee}W"


class SignatureElectrique(models.Model):
    """
    À CONFIRMER : cette table n'apparaît pas encore dans les captures envoyées.
    À faire créer par ta coéquipière si elle n'existe pas encore, ou à ajuster
    ici si elle existe déjà avec des noms de colonnes différents.
    """
    id_appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE
    )
    puissance_min = models.FloatField()
    puissance_max = models.FloatField()
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'signature_electrique'
        managed = False

    def __str__(self):
        return f"{self.id_appareil} : {self.puissance_min}-{self.puissance_max}W"