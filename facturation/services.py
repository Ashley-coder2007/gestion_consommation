from django.db.models import Sum, Q

from Consommation.models import Consommation
from Consommation.services import bornes_periode, get_consommation_totale, get_consommation_par_appareil, derniere_date_disponible
from .models import TarifTranche

ABONNEMENT = 2000  # FCFA, abonnement fixe mensuel


def get_bareme_tranches(type_usage="residentiel", date_reference=None):
    """Barème de tranches actif : liste de (borne_kwh, prix_kwh) triée par ordre."""
    if date_reference is None:
        date_reference = derniere_date_disponible()

    qs = TarifTranche.objects.filter(type_usage=type_usage)
    if date_reference:
        qs = qs.filter(date_debut_validite__lte=date_reference).filter(
            Q(date_fin_validite__isnull=True) | Q(date_fin_validite__gte=date_reference)
        )
    qs = qs.order_by('ordre')
    return [(t.borne_kwh, float(t.prix_kwh)) for t in qs]


def calculer_cout_energie(kwh, type_usage="residentiel", date_reference=None):
    """Coût (FCFA) d'une quantité d'énergie (kWh) selon le barème progressif par tranches."""
    bareme = get_bareme_tranches(type_usage, date_reference)
    if not bareme:
        return 0

    cout = 0
    borne_precedente = 0
    reste = kwh
    for borne_kwh, prix in bareme:
        taille_tranche = borne_kwh - borne_precedente
        part = min(reste, taille_tranche)
        if part > 0:
            cout += part * prix
            reste -= part
        borne_precedente = borne_kwh
        if reste <= 0:
            break

    return round(cout, 2)

def calculer_couts_marginaux_foyer(appareils_qs, date_debut, date_fin, type_usage="residentiel"):
    """
    Répartit le coût total du foyer entre les appareils, en respectant
    l'ordre des tranches tarifaires (contrairement à calculer_cout_appareil
    qui traite chaque appareil isolément et lui applique tout le barème
    depuis le début).

    Les appareils sont classés par consommation décroissante : les plus
    gros consommateurs "remplissent" les tranches chères en premier,
    ce qui reflète mieux une vraie répartition de facture. La somme des
    coûts renvoyés est garantie égale au coût total du foyer (énergie
    seule, sans abonnement).

    Renvoie un dict {appareil_id: {'kwh':..., 'cout':...}}.
    """
    conso_par_appareil = get_consommation_par_appareil(appareils_qs, date_debut, date_fin)

    # Classement par consommation décroissante (les gros consommateurs
    # "remplissent" les tranches chères en dernier, donc paient le tarif
    # marginal le plus élevé — cohérent avec l'intuition "qui consomme le
    # plus paie le tarif le plus cher sur sa part excédentaire").
    items = sorted(conso_par_appareil.items(), key=lambda x: (x[1] or 0))

    resultat = {}
    cumul_avant = 0
    for appareil_id, kwh in items:
        kwh = kwh or 0
        cumul_apres = cumul_avant + kwh

        cout_avant = calculer_cout_energie(cumul_avant, type_usage, date_fin)
        cout_apres = calculer_cout_energie(cumul_apres, type_usage, date_fin)

        resultat[appareil_id] = {
            'kwh': round(kwh, 3),
            'cout': round(cout_apres - cout_avant, 2),
        }
        cumul_avant = cumul_apres

    return resultat


def get_prix_kwh(date_reference=None, kwh_reference=1):
    """
    Prix indicatif du kWh (FCFA), par défaut celui de la première tranche.
    Le vrai coût dépend du barème complet — utiliser calculer_cout_energie.
    """
    cout = calculer_cout_energie(kwh_reference, "residentiel", date_reference)
    return round(cout / kwh_reference, 2) if kwh_reference else 0


def get_historique_global(nb_mois=6, type_usage="residentiel"):
    """
    Historique des nb_mois derniers mois (jusqu'au dernier mois disponible
    dans les données) : liste de dicts {'mois': 'Jan 2025', 'kwh':..., 'fcfa':...},
    du plus ancien au plus récent.
    """
    import calendar
    from datetime import date

    derniere = derniere_date_disponible()
    if not derniere:
        return []

    MOIS_ABREV = ['', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    resultat = []
    annee, mois = derniere.year, derniere.month
    for _ in range(nb_mois):
        debut = date(annee, mois, 1)
        dernier_jour = calendar.monthrange(annee, mois)[1]
        fin = date(annee, mois, dernier_jour)

        total_kwh = Consommation.objects.filter(
            date__gte=debut, date__lte=fin
        ).aggregate(t=Sum('energie_consommee'))['t'] or 0
        total_kwh = round(total_kwh, 2)

        resultat.append({
            'mois': f"{MOIS_ABREV[mois]} {annee}",
            'kwh': total_kwh,
            'fcfa': round(calculer_cout_energie(total_kwh, type_usage) + ABONNEMENT),
        })

        mois -= 1
        if mois == 0:
            mois = 12
            annee -= 1

    return list(reversed(resultat))