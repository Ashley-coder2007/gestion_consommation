from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, FormView
from django.views.decorators.http import require_POST

from .models import Appareil, HistoriqueAppareil
from .forms import AppareilForm
from . import services


from datetime import datetime
from Consommation.services import derniere_date_disponible

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

        date_str = self.request.GET.get("date_filtre")
        try:
            date_selectionnee = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            date_selectionnee = derniere_date_disponible()

        context.update({
            "appareils": services.get_appareils_avec_donnees(qs, date_selectionnee),
            "categories": services.liste_categories(),
            "filtre": filtre,
            "date_filtre": date_selectionnee.strftime("%Y-%m-%d"),
            "nb_actifs": qs.filter(statut=Appareil.Statut.ACTIVE).count(),
            "active_nav": "appareils",
            "actions_recentes": HistoriqueAppareil.objects.order_by("-cree_le")[:15],
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
        appareil = services.creer_appareil(
            nom=form.cleaned_data["nom"],
            categorie=form.cleaned_data["categorie"],
            puissance=form.cleaned_data["puissance"],
            heures_par_jour=form.cleaned_data["heures_par_jour"],
        )

        services.log_action(
            request=self.request,
            action=HistoriqueAppareil.Action.AJOUT,
            appareil=appareil,
            details=(
                f"Catégorie : {appareil.categorie}\n"
                f"Puissance : {appareil.puissance_nominale} W\n"
                f"Heures/jour : {appareil.heures_par_jour}"
            ),
        )

        messages.success(
            self.request,
            f"L'appareil « {appareil.nom} » a été ajouté avec succès."
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        erreurs = []
        for field, errors in form.errors.items():
            for error in errors:
                erreurs.append(f"{field}: {error}")

        if erreurs:
            messages.error(
                self.request,
                f"Erreurs : {' | '.join(erreurs)}"
            )
        else:
            messages.error(
                self.request,
                "Impossible d'ajouter l'appareil. Vérifie les champs du formulaire."
            )

        return redirect(self.success_url)


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
        appareil = self.get_appareil()

        ancien = (
            f"Anciennes valeurs :\n"
            f"Nom : {appareil.nom}\n"
            f"Catégorie : {appareil.categorie}\n"
            f"Puissance : {appareil.puissance_nominale} W\n"
            f"Heures/jour : {appareil.heures_par_jour}"
        )

        appareil = services.modifier_appareil(
            appareil,
            nom=form.cleaned_data["nom"],
            categorie=form.cleaned_data["categorie"],
            puissance=form.cleaned_data["puissance"],
            heures_par_jour=form.cleaned_data["heures_par_jour"],
        )

        nouveau = (
            f"Nouvelles valeurs :\n"
            f"Nom : {appareil.nom}\n"
            f"Catégorie : {appareil.categorie}\n"
            f"Puissance : {appareil.puissance_nominale} W\n"
            f"Heures/jour : {appareil.heures_par_jour}"
        )

        services.log_action(
            request=self.request,
            action=HistoriqueAppareil.Action.MODIFICATION,
            appareil=appareil,
            details=f"{ancien}\n\n{nouveau}",
        )

        messages.success(
            self.request,
            f"L'appareil « {appareil.nom} » a été modifié avec succès."
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        erreurs = []
        for field, errors in form.errors.items():
            for error in errors:
                erreurs.append(f"{field}: {error}")

        if erreurs:
            messages.error(
                self.request,
                f"Erreurs : {' | '.join(erreurs)}"
            )
        else:
            messages.error(
                self.request,
                "Impossible de modifier l'appareil. Vérifie les champs du formulaire."
            )

        return redirect(self.success_url)


@require_POST
def appareil_supprimer(request, pk):
    appareil = get_object_or_404(Appareil, pk=pk)

    appareil_id = appareil.pk
    nom_appareil = appareil.nom

    details = (
        f"Catégorie : {appareil.categorie}\n"
        f"Puissance : {appareil.puissance_nominale} W\n"
        f"Heures/jour : {appareil.heures_par_jour}"
    )

    appareil.delete()

    services.log_action(
        request=request,
        action=HistoriqueAppareil.Action.SUPPRESSION,
        appareil_id=appareil_id,
        nom_appareil=nom_appareil,
        details=details,
    )

    messages.success(
        request,
        f"L'appareil « {nom_appareil} » a été supprimé avec succès."
    )

    return redirect("appareil_list")


def appareil_toggle(request, pk):
    appareil = get_object_or_404(Appareil, pk=pk)
    appareil = services.toggle_statut(appareil)

    if appareil.statut == Appareil.Statut.ACTIVE:
        action = HistoriqueAppareil.Action.ACTIVATION
        texte = "activé"
    else:
        action = HistoriqueAppareil.Action.DESACTIVATION
        texte = "désactivé"

    services.log_action(
        request=request,
        action=action,
        appareil=appareil,
        details=f"L'appareil a été {texte}.",
    )

    messages.success(
        request,
        f"L'appareil « {appareil.nom} » a été {texte} avec succès."
    )

    return redirect("appareil_list")