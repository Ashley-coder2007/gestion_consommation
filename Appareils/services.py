from .models import Appareil

ICONES_PAR_CATEGORIE = {
    "Cuisine": "fa-solid fa-kitchen-set",
    "Climatisation": "fa-solid fa-snowflake",
    "Éclairage": "fa-solid fa-lightbulb",
    "Audiovisuel": "fa-solid fa-tv",
    "Électroménager": "fa-solid fa-blender",
    "Informatique": "fa-solid fa-laptop",
    "Autre": "fa-solid fa-plug",
}


def get_icone(categorie):
    return ICONES_PAR_CATEGORIE.get(categorie, "fa-solid fa-plug")


def appareil_vers_dict(a):
    return {
        "pk": a.pk,
        "nom": a.nom,
        "categorie": a.categorie or "Autre",
        "icone": get_icone(a.categorie),
        "puissance": a.puissance_nominale,
        "heures_par_jour": a.heures_par_jour or 0,
        "actif": a.statut == Appareil.Statut.ACTIVE,
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
    return sorted(
        Appareil.objects.exclude(categorie__isnull=True)
        .values_list("categorie", flat=True).distinct()
    )