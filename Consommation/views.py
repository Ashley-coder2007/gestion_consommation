import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from Appareils.models import Appareil
from Appareils.services import appareil_vers_dict
from . import services

PERIODES = [("jour", "Aujourd'hui"), ("semaine", "7 derniers jours"),
            ("mois", "30 derniers jours"), ("personnalise", "Période personnalisée")]


class ConsommationGlobaleView(TemplateView):
    template_name = "Consommation/consommation_globale.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.request.GET.get("mode", "jour")
        start_date, end_date, jours = services.bornes_periode(self.request, mode)

        appareils_qs = Appareil.objects.all()
        conso_par_appareil = services.get_consommation_par_appareil(appareils_qs, start_date, end_date)

        rows = []
        total_kWh = 0
        puissance_totale = 0
        for a in appareils_qs:
            kwh = round(conso_par_appareil.get(a.pk, 0) or 0, 2)
            rows.append({
                "appareil": appareil_vers_dict(a),
                "conso_kWh": kwh,
                "cout_fcfa": services.calculer_cout_tranches(kwh),
            })
            total_kWh += kwh
            puissance_totale += a.puissance_nominale

        for row in rows:
            row["pct"] = (row["conso_kWh"] / total_kWh * 100) if total_kWh else 0

        context.update({
            "appareils": rows,
            "total_kWh": total_kWh,
            "total_cout": services.calculer_cout_tranches(total_kWh),
            "puissance_totale": puissance_totale,
            "moy_jour": total_kWh / jours if jours else 0,
            "jours": jours,
            "mode": mode,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "label_periode": dict(PERIODES).get(mode, ""),
            "periodes": PERIODES,
            "pie_labels": json.dumps([r["appareil"]["nom"] for r in rows]),
            "pie_data": json.dumps([r["conso_kWh"] for r in rows]),
            "bar_labels": json.dumps([r["appareil"]["nom"] for r in rows]),
            "bar_data": json.dumps([r["conso_kWh"] for r in rows]),
            "active_nav": "consommation",
        })
        return context


class ConsommationAppareilView(TemplateView):
    template_name = "Consommation/consommation_appareil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        a = get_object_or_404(Appareil, pk=kwargs.get("pk"))
        appareil = appareil_vers_dict(a)

        mode = self.request.GET.get("mode", "semaine")
        start_date, end_date, jours = services.bornes_periode(self.request, mode)

        mesures = services.get_mesures_detail(a, start_date, end_date)
        conso_kWh = round(sum(m.energie_consommee for m in mesures), 3)
        conso_jour = round(conso_kWh / jours, 3) if jours else 0

        context.update({
            "appareil": appareil,
            "jours": jours,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "mode": mode,
            "periodes": PERIODES,
            "conso_kWh": conso_kWh,
            "cout_fcfa": services.calculer_cout_tranches(conso_kWh),
            "conso_jour": conso_jour,
            "cout_jour": services.calculer_cout_tranches(conso_jour),
            "label_periode": dict(PERIODES).get(mode, ""),
            "detail_technique": [
                {"label": "Puissance nominale", "valeur": f'{appareil["puissance"]} W'},
                {"label": "Usage quotidien", "valeur": f'{appareil["heures_par_jour"]} h/j'},
                {"label": "Consommation / jour", "valeur": f"{conso_jour} kWh", "color": "#0984e3"},
            ],
            "chart_labels": json.dumps([m.date.strftime("%d/%m") for m in mesures]),
            "chart_data": json.dumps([round(m.energie_consommee, 3) for m in mesures]),
            "active_nav": "consommation",
        })
        return context