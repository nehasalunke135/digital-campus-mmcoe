from django.core.management.base import BaseCommand
from interx.utils import update_expired_opportunities


class Command(BaseCommand):
    help = "Checks opportunities past their deadline and transitions them from PUBLISHED to EXPIRED."

    def handle(self, *args, **options):
        update_expired_opportunities()
        self.stdout.write(self.style.SUCCESS("Successfully updated expired opportunities."))
