# Generated by Django 4.1.5 on 2023-03-10 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0066_alter_ismsschedulecalendarevent_personal_training_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='ismsschedulecalendarevent',
            name='slug',
            field=models.SlugField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='ismsschedulecalendarevent',
            name='schedule_type',
            field=models.CharField(choices=[('MT', 'Meeting'), ('SPE', 'Special Event'), ('PT', 'Personal Training'), ('CS', 'Class')], max_length=3),
        ),
    ]