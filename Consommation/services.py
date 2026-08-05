from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Sum
from .models import Consommation

TARIF = 115  # FCFA/kWh, tarif de base
TARIF_RESIDENTIEL = [(110, 50), (290, 79), (400, 94), (1200, 99)]
TARIF_PROFESSIONNEL = [(110, 84), (290, 92), (600, 99)]


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


def bornes_periode(request, mode):
    today = timezone.now().date()

    if mode == "personnalise":
        try:
            start_date = datetime.strptime(request.GET.get("date_debut", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = today - timedelta(days=6)
        try:
            end_date = datetime.strptime(request.GET.get("date_fin", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            end_date = today
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        jours = (end_date - start_date).days + 1
    else:
        jours = {"jour": 1, "semaine": 7, "mois": 30}.get(mode, 1)
        end_date = today
        start_date = today - timedelta(days=jours - 1)

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