# Generated by Django 4.1.5 on 2023-03-08 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_configuration', '0011_rename_payment_per_class_attendee_customuser_payment_per_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='basic_hourly_wage',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
