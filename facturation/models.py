from django.db import models


class TarifElectrique(models.Model):
    prix_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut_validite = models.DateField()
    date_fin_validite = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'tarifs_electriques'
        verbose_name = 'Tarif électrique'
        verbose_name_plural = 'Tarifs électriques'

    def __str__(self):
        return f"{self.prix_kwh} FCFA/kWh à partir du {self.date_debut_validite}"


class Facture(models.Model):
    class Statut(models.TextChoices):
        PAYEE = 'payée', 'Payée'
        EN_ATTENTE = 'en_attente', 'En attente'

    appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='factures',
        help_text="Null si la facture concerne la consommation globale"
    )
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    cout_total = models.DecimalField(max_digits=12, decimal_places=2)
    date_generation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PAYEE)
    abonnement = models.DecimalField(max_digits=10, decimal_places=2, default=2000)

    class Meta:
        db_table = 'factures'
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-periode_debut']

    def __str__(self):
        cible = self.appareil.nom if self.appareil else "Global"
        return f"Facture {cible} ({self.periode_debut} - {self.periode_fin})"