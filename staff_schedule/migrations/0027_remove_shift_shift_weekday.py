# Generated by Django 4.1.5 on 2023-02-12 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0026_alter_clockin_deduction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shift',
            name='shift_weekday',
        ),
    ]
