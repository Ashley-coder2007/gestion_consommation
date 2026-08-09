from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Sum, Max
from .models import Consommation

TARIF = 115  # FCFA/kWh, tarif de base (fallback si aucun tarif en base)
TARIF_RESIDENTIEL = [(110, 50), (290, 79), (400, 94), (1200, 99)]
TARIF_PROFESSIONNEL = [(110, 84), (290, 92), (600, 99)]




def derniere_date_disponible():
    """
    Point unique de référence pour 'aujourd'hui' dans tout le système.

    MODE ACTUEL (données de test figées) : renvoie la dernière date
    disponible dans Consommation, car les données s'arrêtent au 31/12/2025.

    MODE FUTUR (mesures en temps réel) : remplacer le corps de cette
    fonction par `return timezone.now().date()` une fois le système
    connecté à un flux de mesures live. Aucun autre fichier n'aura besoin
    d'être modifié si tout le code appelle bien cette fonction plutôt que
    de dupliquer sa propre requête ou d'appeler timezone.now() directement.
    """
    dernier = Consommation.objects.aggregate(derniere=Max('date'))['derniere']
    return dernier or timezone.now().date()

def calculer_cout_tranches(kwh, type_usage="residentiel"):
    tranches = TARIF_RESIDENTIEL if type_usage == "residentiel" else TARIF_PROFESSIONNEL
    cout = 0
    reste = kwh
    for taille_tranche, prix in tranches:
        part = min(reste, taille_tranche)
        if part > 0:
            cout += part * prix
            reste -= part
    return cout


def derniere_date_disponible():
    """
    Renvoie la date la plus récente présente dans la table Consommation.
    Sert de référence pour 'aujourd'hui' tant que les données de test
    s'arrêtent au 31/12/2025 plutôt qu'à la date réelle du calendrier.
    """
    resultat = Consommation.objects.aggregate(derniere=Max('date'))
    return resultat['derniere']


def bornes_periode(request, mode):
    """
    Calcule (date_debut, date_fin, nb_jours) selon le mode demandé.
    mode : 'jour' | 'semaine' | 'mois' | 'personnalise'
    Pour 'jour'/'semaine'/'mois', la référence 'aujourd'hui' est la
    dernière date disponible en base (pas la date système réelle).
    """
    reference = derniere_date_disponible() or timezone.now().date()

    if mode == "personnalise":
        try:
            start_date = datetime.strptime(request.GET.get("date_debut", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = reference - timedelta(days=6)
        try:
            end_date = datetime.strptime(request.GET.get("date_fin", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            end_date = reference
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        jours = (end_date - start_date).days + 1
    else:
        jours = {"jour": 1, "semaine": 7, "mois": 30}.get(mode, 1)
        end_date = reference
        start_date = reference - timedelta(days=jours - 1)

    return start_date, end_date, jours


def get_consommation_totale(appareil, date_debut, date_fin):
    total = Consommation.objects.filter(
        appareil=appareil, date__gte=date_debut, date__lte=date_fin
    ).aggregate(total=Sum("energie_consommee"))["total"]
    return round(total or 0, 3)


def get_consommation_par_appareil(appareils_qs, date_debut, date_fin):
    sommes = (
        Consommation.objects
        .filter(appareil__in=appareils_qs, date__gte=date_debut, date__lte=date_fin)
        .values("appareil_id")
        .annotate(total=Sum("energie_consommee"))
    )
    return {s["appareil_id"]: s["total"] for s in sommes}


def get_mesures_detail(appareil, date_debut, date_fin):
    return list(
        Consommation.objects
        .filter(appareil=appareil, date__gte=date_debut, date__lte=date_fin)
        .order_by("date")
    )