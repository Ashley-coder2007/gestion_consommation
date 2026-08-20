from django.db.models.signals import post_save
from django.dispatch import receiver
from Mesures.models import SignalAgrege
from .services.temps_reel_service import diffuser_nouveau_signal


@receiver(post_save, sender=SignalAgrege)
def on_nouveau_signal(sender, instance, created, **kwargs):
    if created:
        diffuser_nouveau_signal(instance)