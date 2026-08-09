from django.db import models


class Appareil(models.Model):
    class TypeCourant(models.TextChoices):
        CONTINU = 'DC', 'Courant continu'
        ALTERNATIF = 'AC', 'Courant alternatif'

    class Statut(models.TextChoices):
        ACTIVE = 'activé', 'Activé'
        DESACTIVE = 'désactivé', 'Désactivé'
    class Categorie(models.TextChoices):
        CUISINE = 'CUISINE', 'Cuisine'
        CLIMATISATION = 'CLIMATISATION', 'Climatisation'
        ECLAIRAGE = 'ECLAIRAGE', 'Eclairage'
        AUDIOVISUEL = 'AUDIOVISUEL', 'Audiovisuel'
        ELECTROMENAGER = 'ELECTROMENAGER', 'Electromenager'
        INFORMATIQUE = 'INFORMATIQUE', 'Informatique'
        AUTRE = 'AUTRE', 'Autre'

    id_appareil = models.AutoField(primary_key=True, db_column="id_appareil")
    nom = models.CharField(max_length=100)
    type_courant = models.CharField(max_length=2, choices=TypeCourant.choices)
    puissance_nominale = models.FloatField(help_text="Puissance nominale en Watts")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIVE)
    categorie = models.CharField(max_length=50, choices=Categorie.choices, null=True, blank=True)
    heures_par_jour = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'appareils'
        managed = False
        verbose_name = 'Appareil'
        verbose_name_plural = 'Appareils'

    def __str__(self):
        return self.nom


    @property
    def _derniere_date_disponible(self):
        from Consommation.services import derniere_date_disponible
        return derniere_date_disponible()

    @property
    def conso_kWh_jour(self):
     from Consommation.models import Consommation
     derniere_date = self._derniere_date_disponible
     if not derniere_date:
        return 0
     c = Consommation.objects.filter(appareil=self, date=derniere_date).first()
     return float(c.energie_consommee) if c else 0


    @property
    def conso_kWh_mois(self):
     from Consommation.models import Consommation
     from django.db.models import Sum
     derniere_date = self._derniere_date_disponible
     if not derniere_date:
        return 0
     total = Consommation.objects.filter(
        appareil=self,
        date__year=derniere_date.year,
        date__month=derniere_date.month
     ).aggregate(t=Sum('energie_consommee'))['t']
     return float(total) if total else 0


    @property
    def cout_mois(self):
     """Coût mensuel estimé en FCFA, basé sur le tarif électrique actuellement en vigueur."""
     from facturation.models import TarifElectrique
     from django.utils import timezone

     aujourd_hui = timezone.now().date()
     tarif = TarifElectrique.objects.filter(
        date_debut_validite__lte=aujourd_hui
     ).filter(
        models.Q(date_fin_validite__isnull=True) | models.Q(date_fin_validite__gte=aujourd_hui)
     ).order_by('-date_debut_validite').first()

     if not tarif:
        return 0
     return float(self.conso_kWh_mois) * float(tarif.prix_kwh)