from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from Mesures.models import MesureFine, SignatureElectrique


class Command(BaseCommand):
    help = "Reconstruit signature_electrique à partir de mesures_fines_jan2010"

    def handle(self, *args, **options):
        appareils_ids = MesureFine.objects.values_list('id_appareil', flat=True).distinct()

        for id_app in appareils_ids:
            stats = MesureFine.objects.filter(
                id_appareil_id=id_app, puissance_active__gt=0
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