# Generated by Django 4.2.7 on 2024-03-11 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0073_remove_food_quantity_sale"),
    ]

    operations = [
        migrations.AddField(
            model_name="food",
            name="quantity_sale",
            field=models.IntegerField(default=0),
        ),
    ]
