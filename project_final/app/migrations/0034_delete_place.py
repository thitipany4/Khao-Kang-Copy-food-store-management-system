# Generated by Django 4.2.7 on 2023-12-20 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0033_alter_place_location"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Place",
        ),
    ]
