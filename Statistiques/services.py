import calendar
from datetime import date
from django.db.models import Sum

from Appareils.models import Appareil
from Consommation.models import Consommation
from Facturation.services import get_prix_kwh

COULEURS_CATEGORIE = {
    "Climatisation": "#0984e3",
    "Électroménager": "#00b894",
    "Informatique": "#00cec9",
    "Audiovisuel": "#74b9ff",
    "Éclairage": "#55efc4",
    "Cuisine": "#fd79a8",
    "Autre": "#a4b0be",
}

MOIS_NOMS = [
    (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
    (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
    (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre"),
]


def liste_mois():
    return MOIS_NOMS


def liste_annees():
    annees = (
        Consommation.objects.dates("date", "year")
        .values_list("date__year", flat=True)
    )
    annees = sorted(set(annees), reverse=True)
    if not annees:
        annees = [date.today().year]
    return annees


def _bornes_mois(annee, mois):
    debut = date(annee, mois, 1)
    dernier_jour = calendar.monthrange(annee, mois)[1]
    fin = date(annee, mois, dernier_jour)
    return debut, fin


def _mois_precedent(annee, mois):
    if mois == 1:
        return annee - 1, 12
    return annee, mois - 1


def get_total_kwh_periode(debut, fin):
    total = Consommation.objects.filter(date__gte=debut, date__lte=fin).aggregate(
        total=Sum("energie_consommee")
    )["total"]
    return round(total or 0, 2)


def get_categories_stats(annee, mois):
    debut, fin = _bornes_mois(annee, mois)

    sommes = (
        Consommation.objects
        .filter(date__gte=debut, date__lte=fin)
        .values("appareil__categorie")
        .annotate(total=Sum("energie_consommee"))
    )
    conso_par_categorie = {
        (s["appareil__categorie"] or "Autre"): (s["total"] or 0) for s in sommes
    }

    total_general = sum(conso_par_categorie.values())
    prix_kwh = get_prix_kwh(fin)

    rows = []
    for categorie, kwh in sorted(conso_par_categorie.items(), key=lambda x: -x[1]):
        kwh = round(kwh, 2)
        nb = Appareil.objects.filter(categorie=categorie).count()
        rows.append({
            "categorie": categorie,
            "nom": categorie,
            "kWh": kwh,
            "fcfa": round(kwh * prix_kwh),
            "nb": nb,
            "pct": round((kwh / total_general * 100), 1) if total_general else 0,
            "color": COULEURS_CATEGORIE.get(categorie, "#a4b0be"),
            "couleur": COULEURS_CATEGORIE.get(categorie, "#a4b0be"),
        })
    return rows


def get_evolution_6_mois(annee, mois):
    """Retourne labels + kWh + FCFA sur les 6 derniers mois, mois sélectionné inclus."""
    mois_points = []
    a, m = annee, mois
    for _ in range(6):
        mois_points.append((a, m))
        a, m = _mois_precedent(a, m)
    mois_points.reverse()

    prix_kwh = get_prix_kwh()
    labels, kwh_data, fcfa_data = [], [], []
    for a, m in mois_points:
        debut, fin = _bornes_mois(a, m)
        kwh = get_total_kwh_periode(debut, fin)
        labels.append(dict(MOIS_NOMS)[m][:3])
        kwh_data.append(kwh)
        fcfa_data.append(round(kwh * prix_kwh))

    return labels, kwh_data, fcfa_data


def get_evolution_pct(annee, mois):
    """Évolution vs le mois précédent (affichage brut '+5.1% vs mois dernier')."""
    debut, fin = _bornes_mois(annee, mois)
    total_courant = get_total_kwh_periode(debut, fin)

    a_prec, m_prec = _mois_precedent(annee, mois)
    debut_prec, fin_prec = _bornes_mois(a_prec, m_prec)
    total_precedent = get_total_kwh_periode(debut_prec, fin_prec)

    if total_precedent:
        return round((total_courant - total_precedent) / total_precedent * 100, 1)
    return 0


def get_moyenne_historique(annee, mois, nb_mois=5):
    """Moyenne de consommation des nb_mois précédant le mois sélectionné (hors mois courant)."""
    a, m = annee, mois
    totaux = []
    for _ in range(nb_mois):
        a, m = _mois_precedent(a, m)
        debut, fin = _bornes_mois(a, m)
        totaux.append(get_total_kwh_periode(debut, fin))
    return sum(totaux) / len(totaux) if totaux else 0


def get_score_efficacite(annee, mois):
    """
    Option 1 : compare la conso du mois à la moyenne des 5 mois précédents.
    - Conso <= moyenne habituelle -> score proche de 100 (bonne gestion)
    - Conso > moyenne habituelle -> score baisse proportionnellement
    """
    total_courant = get_total_kwh_periode(*_bornes_mois(annee, mois))
    moyenne_historique = get_moyenne_historique(annee, mois)

    if moyenne_historique == 0:
        # Pas assez d'historique pour comparer -> score neutre
        return 100

    ecart_pct = (total_courant - moyenne_historique) / moyenne_historique * 100
    score = 100 - ecart_pct
    return max(0, min(100, round(score)))