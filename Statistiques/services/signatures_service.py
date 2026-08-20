from django.core.cache import cache
from Mesures.models import SignatureElectrique


def charger_signatures():
    signatures = cache.get("signatures_appareils")
    if signatures is None:
        signatures = {
            s.id_appareil.nom: {"min": s.puissance_min, "max": s.puissance_max}
            for s in SignatureElectrique.objects.select_related('id_appareil').all()
        }
        cache.set("signatures_appareils", signatures, 3600)  # 1h
    return signatures


def invalider_cache_signatures():
    """À appeler si un admin modifie signature_electrique manuellement."""
    cache.delete("signatures_appareils")