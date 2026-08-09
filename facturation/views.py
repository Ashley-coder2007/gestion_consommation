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
        couts_marginaux = services.calculer_couts_marginaux_foyer(appareils_qs, start_date, end_date)

        rows = []
        total_kWh = 0
        for a in appareils_qs:
            detail = couts_marginaux.get(a.pk, {'kwh': 0, 'cout': 0})
            rows.append({
                "appareil": appareil_vers_dict(a),
                "conso_kWh": detail['kwh'],
                "cout_fcfa": detail['cout'],
            })
            total_kWh += detail['kwh']

        total_energie = services.calculer_cout_energie(total_kWh)
        total_facture = total_energie + services.ABONNEMENT

        context.update({
            "appareils": rows,
            "total_energie": total_energie,
            "abonnement": services.ABONNEMENT,
            "total_facture": total_facture,
            "total_kWh": total_kWh,
            # ... reste inchangé
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

        # Coût marginal réel : calculé sur l'ensemble du foyer, puis on
        # extrait la part de CET appareil dans la répartition globale.
        appareils_qs = Appareil.objects.all()
        couts_marginaux = services.calculer_couts_marginaux_foyer(appareils_qs, start_date, end_date)
        detail = couts_marginaux.get(a.pk, {'kwh': 0, 'cout': 0})

        conso_kWh = detail['kwh']
        conso_jour = round(conso_kWh / jours, 3) if jours else 0
        cout_fcfa = detail['cout']
        cout_jour = round(cout_fcfa / jours, 2) if jours else 0
        prix_kwh = round(cout_fcfa / conso_kWh, 2) if conso_kWh else services.get_prix_kwh()

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
                {"label": "Tarif marginal moyen", "valeur": f"{prix_kwh} FCFA/kWh"},
                {"label": "Coût sur la période", "valeur": f"{cout_fcfa} FCFA", "color": "#00b894"},
            ],
            "chart_labels": json.dumps([f"J{i+1}" for i in range(jours)]),
            "chart_data": json.dumps([round(cout_jour + (i % 3) * 5, 0) for i in range(jours)]),
            "active_nav": "facturation",
        })
        return context