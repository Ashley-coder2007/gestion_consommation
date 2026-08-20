# Mesures/management/commands/rejouer_mois_nilm.py
import time
from django.core.management.base import BaseCommand
from Mesures.models import MesureFine
from Statistiques.nilm_services.temps_reel_service import diffuser_nouveau_signal


class FakeSignal:
    """Simule un objet SignalAgrege à partir d'une ligne de MesureFine,
    pour réutiliser diffuser_nouveau_signal() tel quel."""
    def __init__(self, tick_time, puissance):
        self.tick_time = tick_time
        self.puissance_totale_w = puissance


class Command(BaseCommand):
    help = "Rejoue les mesures fines d'un mois à travers le NILM, en temps accéléré, pour visualisation sur l'interface"

    def add_arguments(self, parser):
        parser.add_argument(
            '--vitesse',
            type=float,
            default=0.1,
            help="Pause en secondes entre chaque point (défaut 0.1s, mets 0.5 pour du vrai temps réel)"
        )
        parser.add_argument(
            '--appareil',
            type=int,
            default=None,
            help="Filtrer sur un seul id_appareil (optionnel)"
        )

    def handle(self, *args, **options):
        vitesse = options['vitesse']
        id_appareil = options['appareil']

        mesures = MesureFine.objects.order_by('tick_time')
        if id_appareil:
            mesures = mesures.filter(id_appareil_id=id_appareil)

        total = mesures.count()
        self.stdout.write(f"Rejeu de {total} points de mesure...")

        for i, mesure in enumerate(mesures.iterator(chunk_size=500)):
            fake_signal = FakeSignal(
                tick_time=mesure.tick_time,
                puissance=mesure.puissance_active
            )
            diffuser_nouveau_signal(fake_signal)

            if i % 100 == 0:
                self.stdout.write(f"{i}/{total} points traités...")

            time.sleep(vitesse)

        self.stdout.write(self.style.SUCCESS(f"Rejeu terminé : {total} points traités."))
