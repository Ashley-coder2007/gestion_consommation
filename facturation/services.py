from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from .models import TarifElectrique, Facture

ABONNEMENT = 2000  # TODO : pas de champ en base, valeur en dur pour l'instant


def get_tarif_actuel(date=None):
    date = date or timezone.now().date()
    return (
        TarifElectrique.objects
        .filter(date_debut_validite__lte=date)
        .filter(Q(date_fin_validite__isnull=True) | Q(date_fin_validite__gte=date))
        .order_by("-date_debut_validite")
        .first()
    )


def get_prix_kwh(date=None):
    tarif = get_tarif_actuel(date)
    return float(tarif.prix_kwh) if tarif else 0


def calculer_cout_energie(kwh, date=None):
    return round(kwh * get_prix_kwh(date))


def get_historique_global(limite=6):
    """Factures globales (appareil=None), avec kWh recalculé depuis Consommation."""
    from Consommation.models import Consommation
    from django.db.models import Sum

    factures = Facture.objects.filter(appareil__isnull=True).order_by("-periode_debut")[:limite]
    rows = []
    for f in factures:
        kwh = Consommation.objects.filter(
            date__gte=f.periode_debut, date__lte=f.periode_fin
        ).aggregate(total=Sum("energie_consommee"))["total"] or 0
        rows.append({
            "mois": f.periode_debut.strftime("%b %Y"),
            "kWh": round(kwh, 1),
            "fcfa": float(f.cout_total),
            "statut": "payée",  # TODO : pas de champ statut en base pour l'instant
        })
    return rows


def creer_facture(appareil, periode_debut, periode_fin, cout_total):
    return Facture.objects.create(
        appareil=appareil,
        periode_debut=periode_debut,
        periode_fin=periode_fin,
        cout_total=cout_total,
    )
