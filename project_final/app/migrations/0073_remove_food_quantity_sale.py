# Generated by Django 4.2.7 on 2024-03-11 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0072_alter_orderitemtype1_total_price_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="food",
            name="quantity_sale",
        ),
    ]
