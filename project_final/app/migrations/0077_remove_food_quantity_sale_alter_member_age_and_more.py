# Generated by Django 4.2.7 on 2024-03-16 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0076_merge_20240311_1414"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="food",
            name="quantity_sale",
        ),
        migrations.AlterField(
            model_name="member",
            name="age",
            field=models.CharField(
                choices=[
                    ("11-20 ปี", "11-20 ปี"),
                    ("21-30 ปี", "21-30 ปี"),
                    ("31-40 ปี", "31-40 ปี"),
                    ("41-50 ปี", "41-50 ปี"),
                    ("51-60 ปี", "51-60 ปี"),
                    ("60 ปีขึ้น", "60 ปีขึ้น"),
                ],
                default="11-20",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="created",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]