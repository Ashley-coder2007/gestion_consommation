from .signatures_service import charger_signatures

_dernier_point = {"puissance": None}
TOLERANCE = 20  # watts, ajustable selon tes tests


def analyser_nilm(puissance_actuelle, tick_time):
    global _dernier_point

    if _dernier_point["puissance"] is None:
        _dernier_point["puissance"] = puissance_actuelle
        return {"evenement": None, "appareil": None, "tick_times": str(tick_time)}

    delta = puissance_actuelle - _dernier_point["puissance"]
    delta_abs = abs(delta)
    _dernier_point["puissance"] = puissance_actuelle

    signatures = charger_signatures()

    meilleur, meilleur_ecart = None, float('inf')
    for nom_appareil, plage in signatures.items():
        centre = (plage["min"] + plage["max"]) / 2
        ecart = abs(delta_abs - centre)
        if ecart < meilleur_ecart:
            meilleur_ecart, meilleur = ecart, nom_appareil

    if meilleur is None or meilleur_ecart > TOLERANCE:
        return {"evenement": None, "appareil": None, "tick_times": str(tick_time)}

    return {
        "evenement": "ON" if delta > 0 else "OFF",
        "appareil": meilleur,
        "tick_times": str(tick_time),
    }