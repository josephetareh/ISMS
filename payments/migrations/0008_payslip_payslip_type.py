# Generated by Django 4.1.5 on 2023-03-06 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_payslip_payment_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='payslip_type',
            field=models.CharField(choices=[('GNL', 'General'), ('OOO', 'One-on-One')], default='GNL', max_length=3),
        ),
    ]
