# Generated by Django 4.2.7 on 2024-02-20 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0061_alter_order_confirm"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="completed",
            field=models.CharField(
                choices=[("incompleted", "ยังไม่สมบุรณ์"), ("completed", "สมบุรณ์")],
                default="incompleted",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="confirm",
            field=models.CharField(
                choices=[
                    ("wait_to_confirm", "รอยืนยัน"),
                    ("confirmed", "ยืนยันเเล้ว"),
                    ("cancel", "ยกเลิก"),
                ],
                default="wait_to_confirm",
                max_length=20,
            ),
        ),
    ]