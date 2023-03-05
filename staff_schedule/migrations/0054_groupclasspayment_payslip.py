# Generated by Django 4.1.5 on 2023-03-05 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payslip_paid'),
        ('staff_schedule', '0053_clockin_payslip'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupclasspayment',
            name='payslip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.payslip'),
        ),
    ]