# Generated by Django 4.1.5 on 2023-03-13 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0011_rename_sessiondetail_sessionexercises'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionexercises',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='sessionexercises',
            name='session',
        ),
        migrations.RemoveField(
            model_name='sessionexercises',
            name='start_time',
        ),
    ]
