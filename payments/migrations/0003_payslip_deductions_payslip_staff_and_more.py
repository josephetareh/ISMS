# Generated by Django 4.1.5 on 2023-03-05 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0002_payslip_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='deductions',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='payslip',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payslip',
            name='total_payment',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
