# Generated by Django 4.1.5 on 2023-03-09 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0062_alter_ismsschedulefixedevent_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ismsschedulefixedevent',
            name='recurring',
        ),
        migrations.RemoveField(
            model_name='ismsschedulefixedevent',
            name='recurring_count',
        ),
        migrations.RemoveField(
            model_name='ismsschedulefixedevent',
            name='recurring_interval',
        ),
    ]
