from django.core.management.base import BaseCommand
from django.conf import settings
from itertools import islice
import csv
from app.models import *

class Command(BaseCommand):
    help = 'load data from csv'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        datafile = settings.BASE_DIR / 'data.csv'

        with open(datafile, 'r') as csvfile:
            render = csv.DictReader(islice(csvfile,1,None))

            for row in render:

                Data.objects.get_or_create(
                    country=row['country'], 
                     pop=float(row['pop']),
                     continent=row['continent'], 
                     lifeExp=float(row['lifeExp']),
                     gdpPercap=float(row['gdpPercap']), 
                )