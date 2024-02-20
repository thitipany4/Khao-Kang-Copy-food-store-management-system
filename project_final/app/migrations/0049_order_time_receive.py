# Generated by Django 4.2.7 on 2024-02-13 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0048_orderitemtype2_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="time_receive",
            field=models.CharField(
                choices=[
                    ("10:00", "10:00 AM"),
                    ("10:30", "10:30 AM"),
                    ("11:00", "11:00 AM"),
                    ("11:30", "11:30 AM"),
                    ("12:00", "12:00 PM"),
                    ("12:30", "12:30 PM"),
                    ("13:00", "01:00 PM"),
                    ("13:30", "01:30 PM"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]