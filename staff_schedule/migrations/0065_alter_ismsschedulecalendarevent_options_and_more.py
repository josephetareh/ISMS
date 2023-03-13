# Generated by Django 4.1.5 on 2023-03-09 19:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0064_calendarevent_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ismsschedulecalendarevent',
            options={'verbose_name': 'ISMS Schedule Calendar Event'},
        ),
        migrations.RemoveField(
            model_name='ismsschedulecalendarevent',
            name='calendar_dates',
        ),
        migrations.AddField(
            model_name='ismsschedulecalendarevent',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ismsschedulecalendarevent',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='CalendarEvent',
        ),
    ]
