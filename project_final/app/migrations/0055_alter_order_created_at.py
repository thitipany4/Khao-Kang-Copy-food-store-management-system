# Generated by Django 4.2.7 on 2024-02-17 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0054_alter_transaction_transaction_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateField(null=True),
        ),
    ]