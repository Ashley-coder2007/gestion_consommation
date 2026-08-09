from django.db import models


class TarifElectrique(models.Model):
    id_tarif = models.AutoField(primary_key=True, db_column='id_tarif')
    prix_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut_validite = models.DateField()
    date_fin_validite = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'tarifs_electriques'
        managed = False
        verbose_name = 'Tarif électrique'
        verbose_name_plural = 'Tarifs électriques'

    def __str__(self):
        return f"{self.prix_kwh} FCFA/kWh à partir du {self.date_debut_validite}"


class Facture(models.Model):
    class Statut(models.TextChoices):
        PAYEE = 'payee', 'Payée'
        EN_ATTENTE = 'en_attente', 'En attente'

    id_facture = models.AutoField(primary_key=True, db_column='id_facture')
    appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='id_appareil',
        related_name='factures',
        help_text="Null si la facture concerne la consommation globale"
    )
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    cout_total = models.DecimalField(max_digits=12, decimal_places=2)
    abonnement = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_generation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'factures'
        managed = False
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-periode_debut']

    def __str__(self):
        cible = self.appareil.nom if self.appareil else "Global"
        return f"Facture {cible} ({self.periode_debut} - {self.periode_fin})"

class TarifTranche(models.Model):
    class TypeUsage(models.TextChoices):
        RESIDENTIEL = 'residentiel', 'Résidentiel'
        PROFESSIONNEL = 'professionnel', 'Professionnel'

    id_tranche = models.AutoField(primary_key=True, db_column='id_tranche')
    type_usage = models.CharField(max_length=20, choices=TypeUsage.choices, default=TypeUsage.RESIDENTIEL)
    ordre = models.SmallIntegerField()
    borne_kwh = models.IntegerField(help_text="Borne haute cumulative de la tranche, en kWh")
    prix_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut_validite = models.DateField()
    date_fin_validite = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'tarifs_tranches'
        managed = False
        verbose_name = 'Tranche tarifaire'
        verbose_name_plural = 'Tranches tarifaires'
        ordering = ['type_usage', 'ordre']

    def __str__(self):
        return f"{self.type_usage} - tranche {self.ordre} (≤{self.borne_kwh} kWh) : {self.prix_kwh} FCFA/kWh"