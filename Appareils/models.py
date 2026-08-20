from django.db import models
from Consommation.services import derniere_date_disponible
from django.conf import settings


class Appareil(models.Model):
    class TypeCourant(models.TextChoices):
        CONTINU = 'DC', 'Courant continu'
        ALTERNATIF = 'AC', 'Courant alternatif'

    class Statut(models.TextChoices):
        ACTIVE = 'activé', 'Activé'
        DESACTIVE = 'désactivé', 'Désactivé'

    class Categorie(models.TextChoices):
        CUISINE = 'Cuisine', 'Cuisine'
        CLIMATISATION = 'Climatisation', 'Climatisation'
        ECLAIRAGE = 'Eclairage', 'Eclairage'
        AUDIOVISUEL = 'Audiovisuel', 'Audiovisuel'
        ELECTROMENAGER = 'Electromenager', 'Electromenager'
        INFORMATIQUE = 'Informatique', 'Informatique'
        AUTRE = 'Autre', 'Autre'

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
        """Coût mensuel estimé en FCFA, basé sur le barème progressif par tranches (facturation.services)."""
        from facturation.services import calculer_cout_energie
        return calculer_cout_energie(self.conso_kWh_mois)

        aujourd_hui = timezone.now().date()
        tarif = TarifElectrique.objects.filter(
            date_debut_validite__lte=aujourd_hui
        ).filter(
            models.Q(date_fin_validite__isnull=True) | models.Q(date_fin_validite__gte=aujourd_hui)
        ).order_by('-date_debut_validite').first()

        if not tarif:
            return 0
        return float(self.conso_kWh_mois) * float(tarif.prix_kwh)


class HistoriqueAppareil(models.Model):
    class Action(models.TextChoices):
        AJOUT = "AJOUT", "Ajout"
        MODIFICATION = "MODIFICATION", "Modification"
        SUPPRESSION = "SUPPRESSION", "Suppression"
        ACTIVATION = "ACTIVATION", "Activation"
        DESACTIVATION = "DESACTIVATION", "Désactivation"

    appareil_id = models.PositiveIntegerField(null=True, blank=True)
    nom_appareil = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=Action.choices)
    details = models.TextField(blank=True)

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "Historique appareil"
        verbose_name_plural = "Historiques appareils"

    def __str__(self):
        return f"{self.get_action_display()} - {self.nom_appareil}"