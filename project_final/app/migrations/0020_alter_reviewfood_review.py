# Generated by Django 4.2.8 on 2023-12-10 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0019_rename_score_reviewfood_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reviewfood",
            name="review",
            field=models.TextField(max_length=500),
        ),
    ]
