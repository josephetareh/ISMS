# Generated by Django 4.1.5 on 2023-01-23 15:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0017_clockin_deduction'),
    ]

    operations = [
        migrations.AddField(
            model_name='clockin',
            name='date_to_clock_in',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 23, 15, 29, 31, 958585, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
