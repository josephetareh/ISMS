# Generated by Django 4.1.5 on 2023-02-12 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0030_rename_shift_weekday_shift_weekday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='weekday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='staff_schedule.weekday'),
        ),
    ]
