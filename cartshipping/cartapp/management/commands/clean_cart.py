# management/commands/clean_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from cartapp.models import Order


class Command(BaseCommand):
    help = 'Delete data older than 30 minutes'

    def handle(self, *args, **options):
        threshold_time = timezone.now() - timezone.timedelta(minutes=2)
        Order.objects.filter(created_at__lt=threshold_time).delete()
        self.stdout.write(self.style.SUCCESS('Data deleted successfully'))
