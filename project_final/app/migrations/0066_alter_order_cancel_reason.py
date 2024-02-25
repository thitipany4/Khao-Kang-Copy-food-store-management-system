# Generated by Django 4.2.7 on 2024-02-25 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0065_order_cancel_reason"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="cancel_reason",
            field=models.CharField(
                blank=True,
                choices=[
                    ("soldout", "สินค้าหมด"),
                    ("cant-call-user", "ไม่สามารถติดต่อลูกค้าได้"),
                    ("user-dont-receive", "ลูกค้าไม่มารับอาหาร"),
                    ("user-cancel", "ลูกค้าเปลี่ยนใจ/ยกเลิกการจอง"),
                    ("cant-receive", "ไม่สามารถไปรับอาหารได้"),
                ],
                max_length=40,
                null=True,
            ),
        ),
    ]