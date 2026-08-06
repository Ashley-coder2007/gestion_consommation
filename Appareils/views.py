from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, FormView

from .models import Appareil
from .forms import AppareilForm
from . import services


class AppareilListView(ListView):
    model = Appareil
    template_name = "Appareils/appareil_list.html"

    def get_queryset(self):
        qs = Appareil.objects.all()
        filtre = self.request.GET.get("categorie")
        if filtre:
            qs = qs.filter(categorie=filtre)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        filtre = self.request.GET.get("categorie")

        context.update({
            "appareils": [services.appareil_vers_dict(a) for a in qs],
            "categories": services.liste_categories(),
            "filtre": filtre,
            "nb_actifs": qs.filter(statut=Appareil.Statut.ACTIVE).count(),
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
        services.creer_appareil(
            nom=form.cleaned_data["nom"],
            categorie=form.cleaned_data["categorie"],
            puissance=form.cleaned_data["puissance"],
            heures_par_jour=form.cleaned_data["heures_par_jour"],
        )
        messages.success(self.request, "Appareil ajouté.")
        return super().form_valid(form)


class AppareilModifierView(FormView):
    template_name = "Appareils/appareil_ajouter.html"
    form_class = AppareilForm
    success_url = reverse_lazy("appareil_list")

    def get_appareil(self):
        return get_object_or_404(Appareil, pk=self.kwargs.get("pk"))

    def get_initial(self):
        a = self.get_appareil()
        return {
            "nom": a.nom,
            "categorie": a.categorie,
            "puissance": a.puissance_nominale,
            "heures_par_jour": a.heures_par_jour,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appareil"] = self.get_appareil()
        context["active_nav"] = "appareils"
        return context

    def form_valid(self, form):
        services.modifier_appareil(
            self.get_appareil(),
            nom=form.cleaned_data["nom"],
            categorie=form.cleaned_data["categorie"],
            puissance=form.cleaned_data["puissance"],
            heures_par_jour=form.cleaned_data["heures_par_jour"],
        )
        messages.success(self.request, "Appareil modifié.")
        return super().form_valid(form)


def appareil_supprimer(request, pk):
    a = get_object_or_404(Appareil, pk=pk)
    a.delete()
    messages.success(request, "Appareil supprimé.")
    return redirect("appareil_list")


def appareil_toggle(request, pk):
    a = get_object_or_404(Appareil, pk=pk)
    services.toggle_statut(a)
    messages.success(request, "Statut basculé.")
    return redirect("appareil_list")