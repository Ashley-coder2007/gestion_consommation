from django.db import models



class Consommation(models.Model):
    appareil = models.ForeignKey(
        'Appareils.Appareil', on_delete=models.CASCADE, related_name='consommations'
    )
    date = models.DateField()
    energie_consommee = models.FloatField(help_text="kWh consommés sur la période")

    class Meta:
        db_table = 'consommations'
        verbose_name = 'Consommation'
        verbose_name_plural = 'Consommations'
        unique_together = ('appareil', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.appareil.nom} - {self.date} : {self.energie_consommee} kWh"



# Create your models here.
