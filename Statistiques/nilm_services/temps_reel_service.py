from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .nilm_service import analyser_nilm


def diffuser_nouveau_signal(signal_agrege):
    resultat_nilm = analyser_nilm(
        puissance_actuelle=signal_agrege.puissance_totale_w,
        tick_time=signal_agrege.tick_time,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "temps_reel",
        {
            "type": "envoyer_donnees",
            "data": {
                "tick_times": str(signal_agrege.tick_time),
                "puissance_total": signal_agrege.puissance_totale_w,
                "nilm": resultat_nilm,
            },
        },
    )