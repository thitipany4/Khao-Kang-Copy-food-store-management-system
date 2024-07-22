from django.core.management.base import BaseCommand
from django.conf import settings
from itertools import islice
import csv
from datetime import datetime
from app.models import *
import pandas as pd

class Command(BaseCommand):
    help = 'load data from excel'

    def handle(self, *args, **options):
        excel_file = 'รายจ่าย2.xlsx' 

        # Read Excel file
        try:
            df = pd.read_excel(excel_file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Excel file not found.'))
            return

        # Iterate over rows and create Transaction objects
        for index, row in df.iterrows():
            # Parse date string to datetime object

            date_obj = pd.to_datetime(row['date'], format='%d/%m/%Y').date()


            tran = Transaction.objects.create(
                name=row['name'],
                price=row['price'],
                amount=row['amount'],
                total_price=row['total_price'],
                date=date_obj,  
                transaction_type='expenses'
            )
        print('successs add file ')