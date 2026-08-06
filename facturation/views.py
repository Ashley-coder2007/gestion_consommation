import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from Appareils.models import Appareil
from Appareils.services import appareil_vers_dict
from Consommation import services as conso_services
from . import services

PERIODES = [("jour", "Aujourd'hui"), ("semaine", "7 derniers jours"),
            ("mois", "30 derniers jours"), ("personnalise", "Période personnalisée")]


class CoutGlobalView(TemplateView):
    template_name = "facturation/cout_global.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.request.GET.get("mode", "mois")
        start_date, end_date, jours = conso_services.bornes_periode(self.request, mode)

        appareils_qs = Appareil.objects.all()
        conso_par_appareil = conso_services.get_consommation_par_appareil(appareils_qs, start_date, end_date)

        rows = []
        total_kWh = 0
        for a in appareils_qs:
            kwh = round(conso_par_appareil.get(a.pk, 0) or 0, 2)
            rows.append({
                "appareil": appareil_vers_dict(a),
                "conso_kWh": kwh,
                "cout_fcfa": services.calculer_cout_energie(kwh),
            })
            total_kWh += kwh

        total_energie = services.calculer_cout_energie(total_kWh)
        total_facture = total_energie + services.ABONNEMENT

        context.update({
            "appareils": rows,
            "total_energie": total_energie,
            "abonnement": services.ABONNEMENT,
            "total_facture": total_facture,
            "total_kWh": total_kWh,
            "jours": jours,
            "mode": mode,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "label_periode": dict(PERIODES).get(mode, ""),
            "periodes": PERIODES,
            "tarif": services.get_prix_kwh(),
            "historique": services.get_historique_global(),
            "chart_labels": json.dumps([h["mois"] for h in reversed(services.get_historique_global())]),
            "chart_data": json.dumps([h["fcfa"] for h in reversed(services.get_historique_global())]),
            "active_nav": "facturation",
        })
        return context


class CoutAppareilView(TemplateView):
    template_name = "facturation/cout_appareil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        a = get_object_or_404(Appareil, pk=kwargs.get("pk"))
        appareil = appareil_vers_dict(a)

        mode = self.request.GET.get("mode", "semaine")
        start_date, end_date, jours = conso_services.bornes_periode(self.request, mode)

        conso_kWh = conso_services.get_consommation_totale(a, start_date, end_date)
        conso_jour = round(conso_kWh / jours, 3) if jours else 0
        cout_fcfa = services.calculer_cout_energie(conso_kWh)
        cout_jour = services.calculer_cout_energie(conso_jour)
        prix_kwh = services.get_prix_kwh()

        context.update({
            "appareil": appareil,
            "jours": jours,
            "mode": mode,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "periodes": PERIODES,
            "label_periode": dict(PERIODES).get(mode, ""),
            "conso_kWh": conso_kWh,
            "cout_fcfa": cout_fcfa,
            "cout_jour": cout_jour,
            "cout_mois_est": cout_jour * 30,
            "cout_an_est": cout_jour * 365,
            "tarif": prix_kwh,
            "detail_calcul": [
                {"label": "Puissance nominale", "valeur": f'{appareil["puissance"]} W'},
                {"label": "Usage quotidien", "valeur": f'{appareil["heures_par_jour"]} h/j'},
                {"label": "Consommation / jour", "valeur": f"{conso_jour} kWh/j", "color": "#0984e3"},
                {"label": "Tarif Socadel", "valeur": f"{prix_kwh} FCFA/kWh"},
                {"label": "Coût sur la période", "valeur": f"{cout_fcfa} FCFA", "color": "#00b894"},
            ],
            "chart_labels": json.dumps([f"J{i+1}" for i in range(jours)]),
            "chart_data": json.dumps([round(cout_jour + (i % 3) * 5, 0) for i in range(jours)]),
            "active_nav": "facturation",
        })
        return context