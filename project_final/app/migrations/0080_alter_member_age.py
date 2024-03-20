# Generated by Django 4.2.7 on 2024-03-17 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0079_alter_recommendus_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="age",
            field=models.CharField(
                choices=[
                    ("ต่ำกว่า 19 ปี", "ต่ำกว่า 19 ปี"),
                    ("20-39 ปี", "20-39 ปี"),
                    ("40-59 ปี", "40-59 ปี"),
                    ("60 ปีขึ้น", "60 ปีขึ้น"),
                ],
                default="ต่ำกว่า 19 ปี",
                max_length=20,
            ),
        ),
    ]
