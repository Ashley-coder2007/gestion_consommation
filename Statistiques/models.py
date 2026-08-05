from django.db import models


class Statistique(models.Model):
    class Periodicite(models.TextChoices):
        JOURNALIERE = 'JOUR', 'Journalière'
        MENSUELLE = 'MOIS', 'Mensuelle'
        ANNUELLE = 'ANNEE', 'Annuelle'

    appareil = models.ForeignKey(
        'Appareils.Appareil',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='statistiques',
        help_text="Null si la statistique concerne le compteur global"
    )
    periodicite = models.CharField(max_length=5, choices=Periodicite.choices)
    date_reference = models.DateField(help_text="Date représentative de la période")
    consommation_moyenne = models.FloatField()
    consommation_max = models.FloatField()
    consommation_min = models.FloatField()

    class Meta:
        db_table = 'statistiques'
        verbose_name = 'Statistique'
        verbose_name_plural = 'Statistiques'
        ordering = ['-date_reference']

    def __str__(self):
        cible = self.appareil.nom if self.appareil else "Global"
        return f"Stats {cible} - {self.date_reference}"


from django.db import models

# Create your models here.
