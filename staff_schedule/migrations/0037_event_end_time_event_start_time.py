# Generated by Django 4.1.5 on 2023-02-21 09:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0036_remove_event_end_time_remove_event_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
