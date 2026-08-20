import threading
import time
from Mesures.models import MesureFine
from .temps_reel_service import diffuser_nouveau_signal


class FakeSignal:
    def __init__(self, tick_time, puissance):
        self.tick_time = tick_time
        self.puissance_totale_w = puissance


def _rejouer(vitesse, id_appareil=None):
    mesures = MesureFine.objects.order_by('tick_time')
    if id_appareil:
        mesures = mesures.filter(id_appareil_id=id_appareil)

    for mesure in mesures.iterator(chunk_size=500):
        fake_signal = FakeSignal(
            tick_time=mesure.tick_time,
            puissance=mesure.puissance_active
        )
        diffuser_nouveau_signal(fake_signal)
        time.sleep(vitesse)


def lancer_rejeu_arriere_plan(vitesse=0.1, id_appareil=None):
    """Lance le rejeu dans un thread séparé, DANS LE MÊME PROCESS que runserver."""
    thread = threading.Thread(target=_rejouer, args=(vitesse, id_appareil), daemon=True)
    thread.start()