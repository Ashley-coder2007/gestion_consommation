from datetime import date
from django.views.generic import TemplateView
from django.http import JsonResponse
from .nilm_services.rejeu_service import lancer_rejeu_arriere_plan

from . import services
from facturation.services import get_prix_kwh


class StatistiqueView(TemplateView):
    template_name = "statistiques/statistique.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        mois = int(self.request.GET.get("mois", today.month))
        annee = int(self.request.GET.get("annee", today.year))

        debut, fin = services._bornes_mois(annee, mois)
        total_kWh_mois = services.get_total_kwh_periode(debut, fin)
        prix_kwh = get_prix_kwh(fin)

        categories_stats = services.get_categories_stats(annee, mois)
        line_labels, line_kWh, line_fcfa = services.get_evolution_6_mois(annee, mois)

        context.update({
            "total_kWh_mois": total_kWh_mois,
            "total_fcfa_mois": round(total_kWh_mois * prix_kwh),
            "evolution_pct": services.get_evolution_pct(annee, mois),
            "score_efficacite": services.get_score_efficacite(annee, mois),

            "mois_liste": services.liste_mois(),
            "annees_liste": services.liste_annees(),
            "mois_selectionne": mois,
            "annee_selectionnee": annee,
            "nom_mois_selectionne": dict(services.MOIS_NOMS).get(mois, ""),

            "categories_stats": categories_stats,

            "chart_labels": __import__("json").dumps(line_labels),
            "chart_kwh_data": __import__("json").dumps(line_kWh),
            "chart_fcfa_data": __import__("json").dumps(line_fcfa),

            "donut_labels": __import__("json").dumps([c["nom"] for c in categories_stats]),
            "donut_data": __import__("json").dumps([c["kWh"] for c in categories_stats]),
            "donut_colors": __import__("json").dumps([c["color"] for c in categories_stats]),

            "active_nav": "statistiques",
        })
        return context



    def lancer_nilm_demo(request):
    vitesse = float(request.GET.get("vitesse", 0.1))
    lancer_rejeu_arriere_plan(vitesse=vitesse)
    return JsonResponse({"status": "démarré", "vitesse": vitesse})