# Generated by Django 4.1.5 on 2023-02-21 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0035_disputeattachment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='event',
            name='start_time',
        ),
    ]