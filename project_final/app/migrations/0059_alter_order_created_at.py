# Generated by Django 4.2.7 on 2024-02-18 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0058_alter_order_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
