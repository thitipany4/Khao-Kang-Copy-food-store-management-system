# Generated by Django 4.2.7 on 2024-03-20 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0086_cancelreason_timereceive"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cancelreason",
            old_name="user_with",
            new_name="use_with",
        ),
    ]
