import json
from django.views.generic import TemplateView

PERIODES = [("jour", "Aujourd'hui"), ("semaine", "7 derniers jours"),
            ("mois", "30 derniers jours"), ("personnalise", "Période personnalisée")]

APPAREILS_MOCK = [
    {"pk": 1, "nom": "Climatiseur Salon", "categorie": "Climatisation", "icone": "❄️", "puissance": 1500, "heures_par_jour": 8},
    {"pk": 2, "nom": "Climatiseur Chambre", "categorie": "Climatisation", "icone": "❄️", "puissance": 1200, "heures_par_jour": 6},
    {"pk": 3, "nom": "Réfrigérateur", "categorie": "Électroménager", "icone": "🧊", "puissance": 150, "heures_par_jour": 24},
    {"pk": 4, "nom": "Machine à laver", "categorie": "Électroménager", "icone": "🧺", "puissance": 2000, "heures_par_jour": 1.5},
    {"pk": 5, "nom": "Ordinateur + Écran", "categorie": "Informatique", "icone": "💻", "puissance": 250, "heures_par_jour": 5},
    {"pk": 6, "nom": 'Téléviseur 55"', "categorie": "Audiovisuel", "icone": "📺", "puissance": 120, "heures_par_jour": 6},
    {"pk": 7, "nom": "Éclairage (8 ampoules LED)", "categorie": "Éclairage", "icone": "💡", "puissance": 64, "heures_par_jour": 5},
]

TARIF = 115  # FCFA/kWh


def _jours_pour_mode(mode):
    return {"jour": 1, "semaine": 7, "mois": 30, "personnalise": 7}.get(mode, 1)


class ConsommationGlobaleView(TemplateView):
    template_name = "Consommation/consommation_globale.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.request.GET.get("mode", "jour")
        jours = _jours_pour_mode(mode)

        rows = []
        total_kWh = 0
        puissance_totale = 0
        for a in APPAREILS_MOCK:
            kwh = round((a["puissance"] * a["heures_par_jour"] / 1000) * jours, 2)
            rows.append({"appareil": a, "conso_kWh": kwh, "cout_fcfa": kwh * TARIF})
            total_kWh += kwh
            puissance_totale += a["puissance"]

        for row in rows:
            row["pct"] = (row["conso_kWh"] / total_kWh * 100) if total_kWh else 0

        context.update({
            "appareils": rows,
            "total_kWh": total_kWh,
            "total_cout": total_kWh * TARIF,
            "puissance_totale": puissance_totale,
            "moy_jour": total_kWh / jours if jours else 0,
            "jours": jours,
            "mode": mode,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "label_periode": dict(PERIODES).get(mode, ""),
            "periodes": PERIODES,
            "pie_labels": json.dumps([a["nom"] for a in APPAREILS_MOCK]),
            "pie_data": json.dumps([r["conso_kWh"] for r in rows]),
            "bar_labels": json.dumps([a["nom"] for a in APPAREILS_MOCK]),
            "bar_data": json.dumps([r["conso_kWh"] for r in rows]),
            "active_nav": "consommation",
        })
        return context


class ConsommationAppareilView(TemplateView):
    template_name = "Consommation/consommation_appareil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get("pk")
        appareil = next((a for a in APPAREILS_MOCK if a["pk"] == pk), APPAREILS_MOCK[0])

        mode = self.request.GET.get("mode", "semaine")
        jours = _jours_pour_mode(mode)

        conso_jour = round(appareil["puissance"] * appareil["heures_par_jour"] / 1000, 3)
        conso_kWh = round(conso_jour * jours, 3)

        context.update({
            "appareil": appareil,
            "jours": jours,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "mode": mode,
            "periodes": PERIODES,
            "conso_kWh": conso_kWh,
            "cout_fcfa": conso_kWh * TARIF,
            "conso_jour": conso_jour,
            "cout_jour": conso_jour * TARIF,
            "label_periode": dict(PERIODES).get(mode, ""),
            "detail_technique": [
                {"label": "Puissance nominale", "valeur": f'{appareil["puissance"]} W'},
                {"label": "Usage quotidien", "valeur": f'{appareil["heures_par_jour"]} h/j'},
                {"label": "Consommation / jour", "valeur": f"{conso_jour} kWh", "color": "#0984e3"},
            ],
            "chart_labels": json.dumps([f"J{i+1}" for i in range(jours)]),
            "chart_data": json.dumps([round(conso_jour + (i % 3) * 0.05, 3) for i in range(jours)]),
            "active_nav": "consommation",
        })
        return context