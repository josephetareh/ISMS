# Generated by Django 4.1.5 on 2023-01-19 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0014_remove_shift_end_time_remove_shift_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='clockin',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
