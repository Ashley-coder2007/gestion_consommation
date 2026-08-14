from .models import Appareil, HistoriqueAppareil
from Consommation.models import Consommation
import calendar
from django.db.models import Sum
from facturation.services import calculer_couts_marginaux_foyer

ICONES_PAR_CATEGORIE = {
    "CUISINE": "fa-solid fa-kitchen-set",
    "CLIMATISATION": "fa-solid fa-snowflake",
    "ECLAIRAGE": "fa-solid fa-lightbulb",
    "AUDIOVISUEL": "fa-solid fa-tv",
    "ELECTROMENAGER": "fa-solid fa-blender",
    "INFORMATIQUE": "fa-solid fa-laptop",
    "AUTRE": "fa-solid fa-plug",
}

LABELS_CATEGORIE = {
    "CUISINE": "Cuisine",
    "CLIMATISATION": "Climatisation",
    "ECLAIRAGE": "Éclairage",
    "AUDIOVISUEL": "Audiovisuel",
    "ELECTROMENAGER": "Électroménager",
    "INFORMATIQUE": "Informatique",
    "AUTRE": "Autre",
}


def normaliser_categorie(categorie):
    """Met tout en majuscules pour comparer sans tenir compte de la casse."""
    return (categorie or "").strip().upper()


def get_icone(categorie):
    return ICONES_PAR_CATEGORIE.get(normaliser_categorie(categorie), "fa-solid fa-plug")


def get_label_categorie(categorie):
    return LABELS_CATEGORIE.get(normaliser_categorie(categorie), categorie or "Autre")


def calculer_cout_mensuel(kwh_mois, type_usage="residentiel"):
    kwh_mois = float(kwh_mois or 0)
    cout_total = 0

    if type_usage == "residentiel":
        t1 = min(kwh_mois, 110)
        if t1 > 0: cout_total += t1 * 50
        t2 = min(max(kwh_mois - 110, 0), 220)
        if t2 > 0: cout_total += t2 * 79
        t3 = min(max(kwh_mois - 400, 0), 400)
        if t3 > 0: cout_total += t3 * 94
        t4 = min(max(kwh_mois - 800, 0), 1200)
        if t4 > 0: cout_total += t4 * 94
    else:
        t1 = min(kwh_mois, 110)
        if t1 > 0: cout_total += t1 * 84
        t2 = min(max(kwh_mois - 110, 0), 290)
        if t2 > 0: cout_total += t2 * 92
        t3 = min(max(kwh_mois - 400, 0), 600)
        if t3 > 0: cout_total += t3 * 99

    return cout_total


def appareil_vers_dict(a):
    puissance = float(a.puissance_nominale or 0)
    heures = float(a.heures_par_jour or 0)

    conso_kwh_mois = ((puissance * heures) / 1000) * 30
    cout_mois = calculer_cout_mensuel(conso_kwh_mois, "residentiel")

    cat_raw = a.categorie or "Autre"

    return {
        "pk": a.pk,
        "nom": a.nom,
        "categorie": get_label_categorie(cat_raw),
        "categorie_raw": cat_raw,
        "icone": get_icone(cat_raw),
        "puissance": a.puissance_nominale,
        "heures_par_jour": a.heures_par_jour or 0,
        "actif": a.statut == "activé",
        "conso_kWh_mois": conso_kwh_mois,
        "cout_mois": cout_mois,
    }


def creer_appareil(nom, categorie, puissance, heures_par_jour):
    return Appareil.objects.create(
        nom=nom,
        categorie=categorie,
        puissance_nominale=puissance,
        heures_par_jour=heures_par_jour,
        type_courant=Appareil.TypeCourant.ALTERNATIF,
        statut=Appareil.Statut.ACTIVE,
    )


def modifier_appareil(appareil, nom, categorie, puissance, heures_par_jour):
    appareil.nom = nom
    appareil.categorie = categorie
    appareil.puissance_nominale = puissance
    appareil.heures_par_jour = heures_par_jour
    appareil.save()
    return appareil


def toggle_statut(appareil):
    appareil.statut = (
        Appareil.Statut.DESACTIVE if appareil.statut == Appareil.Statut.ACTIVE
        else Appareil.Statut.ACTIVE
    )
    appareil.save()
    return appareil


def liste_categories():
    cats_brutes = sorted(
        Appareil.objects.exclude(categorie__isnull=True)
        .values_list("categorie", flat=True)
        .distinct()
    )
    return [(c, get_label_categorie(c)) for c in cats_brutes]


def log_action(request, action, appareil=None, appareil_id=None, nom_appareil="", details=""):
    utilisateur = None

    if request is not None and hasattr(request, "user"):
        if request.user.is_authenticated:
            utilisateur = request.user

    return HistoriqueAppareil.objects.create(
        appareil_id=appareil.pk if appareil is not None else appareil_id,
        nom_appareil=appareil.nom if appareil is not None else nom_appareil,
        action=action,
        details=details,
        utilisateur=utilisateur,
    )

def get_appareils_avec_donnees(appareils_qs, date_selectionnee):
    """
    Construit la liste de dicts pour l'affichage, en calculant l'usage/jour,
    la consommation mensuelle et le coût mensuel à partir des vraies données
    de Consommation, pour le jour/mois contenant date_selectionnee.
    """


    debut_mois = date_selectionnee.replace(day=1)
    dernier_jour = calendar.monthrange(date_selectionnee.year, date_selectionnee.month)[1]
    fin_mois = date_selectionnee.replace(day=dernier_jour)

    # Conso du jour précis, par appareil
    conso_jour = {
        s["appareil_id"]: s["total"]
        for s in Consommation.objects.filter(date=date_selectionnee)
            .values("appareil_id").annotate(total=Sum("energie_consommee"))
    }

    # Coût marginal réel du mois, par appareil (kwh + cout déjà calculés ensemble)
    couts_mois = calculer_couts_marginaux_foyer(appareils_qs, debut_mois, fin_mois)

    resultat = []
    for a in appareils_qs:
        puissance = float(a.puissance_nominale or 0)
        kwh_jour = float(conso_jour.get(a.pk, 0) or 0)
        usage_jour_h = (kwh_jour * 1000 / puissance) if puissance else 0

        detail_mois = couts_mois.get(a.pk, {'kwh': 0, 'cout': 0})

        cat_raw = a.categorie or "Autre"

        resultat.append({
            "pk": a.pk,
            "nom": a.nom,
            "categorie": get_label_categorie(cat_raw),
            "categorie_raw": cat_raw,
            "icone": get_icone(cat_raw),
            "puissance": a.puissance_nominale,
            "heures_par_jour": round(usage_jour_h, 2),
            "actif": a.statut == "activé",
            "conso_kWh_mois": detail_mois['kwh'],
            "cout_mois": detail_mois['cout'],
        })
    return resultat