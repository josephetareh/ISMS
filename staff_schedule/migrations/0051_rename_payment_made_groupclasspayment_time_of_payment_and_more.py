# Generated by Django 4.1.5 on 2023-02-28 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0050_groupclasspayment_payment_made_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groupclasspayment',
            old_name='payment_made',
            new_name='time_of_payment',
        ),
        migrations.AddField(
            model_name='groupclasspayment',
            name='class_paid_for',
            field=models.BooleanField(default=False),
        ),
    ]
