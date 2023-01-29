# Generated by Django 4.1.5 on 2023-01-24 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0021_clockin_active_alter_clockin_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clockin',
            old_name='date_to_clock_in',
            new_name='shift_ends',
        ),
        migrations.AddField(
            model_name='clockin',
            name='shift_starts',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]