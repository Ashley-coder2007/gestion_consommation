from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, FormView

from .forms import AppareilForm


# ── Données factices (mock) — à remplacer par le vrai model Appareil ──
APPAREILS_MOCK = [
    {"pk": 1, "nom": "Climatiseur Salon", "categorie": "Climatisation", "icone": "❄️",
     "puissance": 1500, "heures_par_jour": 8, "actif": True,
     "conso_kWh_mois": 360.0, "cout_mois": 41400},
    {"pk": 2, "nom": "Réfrigérateur", "categorie": "Électroménager", "icone": "🧊",
     "puissance": 150, "heures_par_jour": 24, "actif": True,
     "conso_kWh_mois": 108.0, "cout_mois": 12420},
    {"pk": 3, "nom": 'Téléviseur 55"', "categorie": "Audiovisuel", "icone": "📺",
     "puissance": 120, "heures_par_jour": 6, "actif": True,
     "conso_kWh_mois": 21.6, "cout_mois": 2484},
    {"pk": 4, "nom": "Machine à laver", "categorie": "Électroménager", "icone": "🧺",
     "puissance": 2000, "heures_par_jour": 1.5, "actif": True,
     "conso_kWh_mois": 90.0, "cout_mois": 10350},
    {"pk": 5, "nom": "Éclairage (8 ampoules LED)", "categorie": "Éclairage", "icone": "💡",
     "puissance": 64, "heures_par_jour": 5, "actif": True,
     "conso_kWh_mois": 9.6, "cout_mois": 1104},
]


class AppareilListView(TemplateView):
    template_name = "Appareils/appareil_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtre = self.request.GET.get("categorie")
        appareils = APPAREILS_MOCK
        if filtre:
            appareils = [a for a in appareils if a["categorie"] == filtre]

        context.update({
            "appareils": appareils,
            "categories": sorted({a["categorie"] for a in APPAREILS_MOCK}),
            "filtre": filtre,
            "nb_actifs": sum(1 for a in APPAREILS_MOCK if a["actif"]),
            "active_nav": "appareils",
        })
        return context


class AppareilAjouterView(FormView):
    template_name = "Appareils/appareil_ajouter.html"
    form_class = AppareilForm
    success_url = reverse_lazy("appareil_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appareil"] = None
        context["active_nav"] = "appareils"
        return context

    def form_valid(self, form):
        # ⚠️ Démo : ne sauvegarde pas encore réellement.
        # Une fois le model Appareil branché :
        #   Appareil.objects.create(**form.cleaned_data)
        messages.success(self.request, "Appareil ajouté (démo — pas encore relié à la base).")
        return super().form_valid(form)


class AppareilModifierView(FormView):
    template_name = "Appareils/appareil_ajouter.html"
    form_class = AppareilForm
    success_url = reverse_lazy("appareil_list")

    def get_appareil(self):
        pk = self.kwargs.get("pk")
        return next((a for a in APPAREILS_MOCK if a["pk"] == pk), APPAREILS_MOCK[0])

    def get_initial(self):
        appareil = self.get_appareil()
        return {
            "nom": appareil["nom"],
            "categorie": appareil["categorie"],
            "puissance": appareil["puissance"],
            "heures_par_jour": appareil["heures_par_jour"],
            "icone": appareil["icone"],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appareil"] = self.get_appareil()
        context["active_nav"] = "appareils"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Appareil modifié (démo).")
        return super().form_valid(form)


def appareil_supprimer(request, pk):
    messages.success(request, "Appareil supprimé (démo).")
    return redirect("appareil_list")


def appareil_toggle(request, pk):
    messages.success(request, "Statut basculé (démo).")
    return redirect("appareil_list")