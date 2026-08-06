from django.db import models

from django.views.generic import TemplateView
from Appareils.models import Appareil

ABONNEMENT_MOIS = 2000

class AccueilView(TemplateView):
    template_name = 'accueil.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        actifs = list(Appareil.objects.filter(actif=True))

        total_kWh_mois = sum(a.conso_kWh_mois for a in actifs)

        top = sorted(actifs, key=lambda a: a.conso_kWh_mois, reverse=True)[:3]
        top_appareils = [
            {
                'appareil': a,
                'kWh':  round(a.conso_kWh_mois, 1),
                'fcfa': round(a.cout_mois),
                'pct':  round(a.conso_kWh_mois / total_kWh_mois * 100) if total_kWh_mois else 0,
            }
            for a in top
        ]

        ctx.update({
            'active_nav':      'accueil',
            'nb_actifs':       len(actifs),
            'nb_total':        Appareil.objects.count(),
            'total_kWh_jour':  sum(a.conso_kWh_jour for a in actifs),
            'total_kWh_mois':  total_kWh_mois,
            'total_cout_mois': sum(a.cout_mois for a in actifs) + ABONNEMENT_MOIS,
            'top_appareils':   top_appareils,
        })
        return ctx