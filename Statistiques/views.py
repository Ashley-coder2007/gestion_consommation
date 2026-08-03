import json
from django.views.generic import TemplateView

APPAREILS_MOCK = [
    {"nom": "Climatiseur Salon", "icone": "❄️", "kWh": 360.0, "fcfa": 41400, "pct": 43},
    {"nom": "Climatiseur Chambre", "icone": "❄️", "kWh": 192.0, "fcfa": 22080, "pct": 23},
    {"nom": "Réfrigérateur", "icone": "🧊", "kWh": 108.0, "fcfa": 12420, "pct": 13},
    {"nom": "Machine à laver", "icone": "🧺", "kWh": 90.0, "fcfa": 10350, "pct": 11},
    {"nom": "Ordinateur + Écran", "icone": "💻", "kWh": 59.4, "fcfa": 6831, "pct": 7},
]

CATEGORIES_MOCK = [
    {"categorie": "Climatisation", "kWh": 549, "fcfa": 63135, "nb": 2, "pct": 65.5, "color": "#0984e3"},
    {"categorie": "Électroménager", "kWh": 198, "fcfa": 22770, "nb": 2, "pct": 23.6, "color": "#00b894"},
    {"categorie": "Informatique", "kWh": 59.4, "fcfa": 6831, "nb": 1, "pct": 7.1, "color": "#00cec9"},
    {"categorie": "Audiovisuel", "kWh": 21.6, "fcfa": 2484, "nb": 1, "pct": 2.6, "color": "#74b9ff"},
    {"categorie": "Éclairage", "kWh": 9.6, "fcfa": 1104, "nb": 1, "pct": 1.2, "color": "#55efc4"},
]


class StatistiqueView(TemplateView):
    template_name = "Statistiques/statistique.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "nb_appareils": 8,
            "nb_actifs": 7,
            "total_kWh_mois": 838,
            "total_fcfa_mois": 99174,
            "score_efficacite": 62,
            "evolution_pct": 5.1,
            "par_categorie": CATEGORIES_MOCK,
            "top_consommateurs": [
                {"appareil": {"nom": a["nom"], "icone": a["icone"]}, "kWh": a["kWh"], "fcfa": a["fcfa"], "pct": a["pct"]}
                for a in APPAREILS_MOCK
            ],
            "line_labels": json.dumps(["Fév", "Mar", "Avr", "Mai", "Jun", "Jul"]),
            "line_kWh": json.dumps([203, 219, 241, 254, 268, 254]),
            "line_fcfa": json.dumps([28545, 30585, 33165, 34830, 36420, 34830]),
            "bar_cat_labels": json.dumps([c["categorie"] for c in CATEGORIES_MOCK]),
            "bar_cat_kWh": json.dumps([c["kWh"] for c in CATEGORIES_MOCK]),
            "pie_labels": json.dumps([c["categorie"] for c in CATEGORIES_MOCK]),
            "pie_data": json.dumps([c["kWh"] for c in CATEGORIES_MOCK]),
            "active_nav": "statistiques",
        })
        return context