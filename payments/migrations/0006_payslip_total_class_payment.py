# Generated by Django 4.1.5 on 2023-03-05 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_payslip_final_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='total_class_payment',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
