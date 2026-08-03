import json
from django.views.generic import TemplateView

PERIODES = [("jour", "Aujourd'hui"), ("semaine", "7 derniers jours"),
            ("mois", "30 derniers jours"), ("personnalise", "Période personnalisée")]

APPAREILS_MOCK = [
    {"pk": 1, "nom": "Climatiseur Salon", "categorie": "Climatisation", "icone": "❄️", "puissance": 1500, "heures_par_jour": 8},
    {"pk": 2, "nom": "Réfrigérateur", "categorie": "Électroménager", "icone": "🧊", "puissance": 150, "heures_par_jour": 24},
    {"pk": 3, "nom": 'Téléviseur 55"', "categorie": "Audiovisuel", "icone": "📺", "puissance": 120, "heures_par_jour": 6},
    {"pk": 4, "nom": "Machine à laver", "categorie": "Électroménager", "icone": "🧺", "puissance": 2000, "heures_par_jour": 1.5},
    {"pk": 5, "nom": "Éclairage (8 ampoules LED)", "categorie": "Éclairage", "icone": "💡", "puissance": 64, "heures_par_jour": 5},
]

TARIF = 115
ABONNEMENT = 2000

HISTORIQUE_MOCK = [
    {"mois": "Jul 2025", "kWh": 254, "fcfa": 34830, "statut": "payée"},
    {"mois": "Jun 2025", "kWh": 268, "fcfa": 36420, "statut": "payée"},
    {"mois": "Mai 2025", "kWh": 241, "fcfa": 33165, "statut": "payée"},
    {"mois": "Avr 2025", "kWh": 219, "fcfa": 30585, "statut": "payée"},
    {"mois": "Mar 2025", "kWh": 203, "fcfa": 28545, "statut": "payée"},
    {"mois": "Fév 2025", "kWh": 187, "fcfa": 26205, "statut": "payée"},
]


def _jours_pour_mode(mode):
    return {"jour": 1, "semaine": 7, "mois": 30, "personnalise": 7}.get(mode, 30)


class CoutGlobalView(TemplateView):
    template_name = "facturation/cout_global.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.request.GET.get("mode", "mois")
        jours = _jours_pour_mode(mode)

        rows = []
        total_kWh = 0
        for a in APPAREILS_MOCK:
            kwh = round((a["puissance"] * a["heures_par_jour"] / 1000) * jours, 2)
            rows.append({"appareil": a, "conso_kWh": kwh, "cout_fcfa": round(kwh * TARIF)})
            total_kWh += kwh

        total_energie = round(total_kWh * TARIF)
        total_facture = total_energie + ABONNEMENT

        context.update({
            "appareils": rows,
            "total_energie": total_energie,
            "abonnement": ABONNEMENT,
            "total_facture": total_facture,
            "total_kWh": total_kWh,
            "jours": jours,
            "mode": mode,
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "label_periode": dict(PERIODES).get(mode, ""),
            "periodes": PERIODES,
            "tarif": TARIF,
            "historique": HISTORIQUE_MOCK,
            "chart_labels": json.dumps([h["mois"] for h in reversed(HISTORIQUE_MOCK)]),
            "chart_data": json.dumps([h["fcfa"] for h in reversed(HISTORIQUE_MOCK)]),
            "active_nav": "facturation",
        })
        return context


class CoutAppareilView(TemplateView):
    template_name = "facturation/cout_appareil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get("pk")
        appareil = next((a for a in APPAREILS_MOCK if a["pk"] == pk), APPAREILS_MOCK[0])

        mode = self.request.GET.get("mode", "semaine")
        jours = _jours_pour_mode(mode)

        conso_jour = round(appareil["puissance"] * appareil["heures_par_jour"] / 1000, 3)
        conso_kWh = round(conso_jour * jours, 3)
        cout_fcfa = round(conso_kWh * TARIF)
        cout_jour = round(conso_jour * TARIF)

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
            "tarif": TARIF,
            "detail_calcul": [
                {"label": "Puissance nominale", "valeur": f'{appareil["puissance"]} W'},
                {"label": "Usage quotidien", "valeur": f'{appareil["heures_par_jour"]} h/j'},
                {"label": "Consommation / jour", "valeur": f"{conso_jour} kWh/j", "color": "#0984e3"},
                {"label": "Tarif Socadel", "valeur": f"{TARIF} FCFA/kWh"},
                {"label": "Coût sur la période", "valeur": f"{cout_fcfa} FCFA", "color": "#00b894"},
            ],
            "chart_labels": json.dumps([f"J{i+1}" for i in range(jours)]),
            "chart_data": json.dumps([round(cout_jour + (i % 3) * 5, 0) for i in range(jours)]),
            "active_nav": "facturation",
        })
        return context