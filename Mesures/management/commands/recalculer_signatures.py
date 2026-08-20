# Mesures/management/commands/recalculer_signatures.py
from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from Mesures.models import Mesure, MesureAppareil, SignatureElectrique


class Command(BaseCommand):
    help = "Reconstruit signature_electrique à partir des mesures fines"

    def handle(self, *args, **options):
        # Liste des appareils distincts présents dans les mesures
        appareils_ids = MesureAppareil.objects.values_list('appareil_id', flat=True).distinct()

        for id_app in appareils_ids:
            stats = Mesure.objects.filter(
                mesures_appareils__appareil_id=id_app,
                puissance_active__gt=0
            ).aggregate(mn=Min('puissance_active'), mx=Max('puissance_active'))

            if stats["mn"] is None:
                continue

            SignatureElectrique.objects.update_or_create(
                id_appareil_id=id_app,
                defaults={
                    "puissance_min": stats["mn"],
                    "puissance_max": stats["mx"],
                }
            )
            self.stdout.write(f"Signature mise à jour pour appareil {id_app}")

        self.stdout.write(self.style.SUCCESS("Signatures recalculées avec succès."))