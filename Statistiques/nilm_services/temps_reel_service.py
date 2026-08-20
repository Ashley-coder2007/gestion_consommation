from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .nilm_service import analyser_nilm
from Mesures.models import EstimationNilm


def diffuser_nouveau_signal(signal_agrege):
    resultat_nilm = analyser_nilm(
        puissance_actuelle=signal_agrege.puissance_totale_w,
        tick_time=signal_agrege.tick_time,
    )

    # Sauvegarde en base UNIQUEMENT si un événement a été détecté
    # (sinon on remplirait la table à chaque tick de 0.5s, même sans événement)
    if resultat_nilm["evenement"] is not None:
        EstimationNilm.objects.create(
            tick_time=signal_agrege.tick_time,
            id_appareil_id=_trouver_id_appareil(resultat_nilm["appareil"]),
            puissance_estimee=signal_agrege.puissance_totale_w,
        )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "temps_reel",
        {
            "type": "envoyer_donnees",
            "data": {
                "tick_times": signal_agrege.tick_time.isoformat(),
                "puissance_total": float(signal_agrege.puissance_totale_w),
                "nilm": resultat_nilm,
            },
        },
    )


def _trouver_id_appareil(nom_appareil):
    from Appareils.models import Appareil
    appareil = Appareil.objects.filter(nom=nom_appareil).first()
    return appareil.id_appareil if appareil else None