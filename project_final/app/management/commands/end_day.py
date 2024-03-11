# In your app's management/commands folder, create a new Python file, e.g., update_options.py
from django.core.management.base import BaseCommand
from app.models import Historysale
from django.utils import timezone
class Command(BaseCommand):
    help = 'Updates options field to None when the time is 2 am'

    def handle(self, *args, **kwargs):
        current_datetime = timezone.now()
        current_date = current_datetime.date()
        print(current_datetime.hour)
        if current_datetime.hour == 6:  # Check if the current hour is 2 PM
            instances = Historysale.objects.filter(date_field=current_date)
            for instance in instances:
                instance.options = 'ไม่ได้เลือก'
                instance.save()
