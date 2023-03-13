# Generated by Django 4.1.5 on 2023-03-09 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0061_rename_ismsschedule_ismsschedulefixedevent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ismsschedulefixedevent',
            options={'verbose_name': 'ISMS Schedule Fixed Event'},
        ),
        migrations.AlterField(
            model_name='ismsschedulefixedevent',
            name='schedule_day',
            field=models.CharField(blank=True, choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], max_length=1),
        ),
    ]