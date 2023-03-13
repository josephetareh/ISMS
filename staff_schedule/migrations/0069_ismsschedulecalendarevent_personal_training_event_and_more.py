# Generated by Django 4.1.5 on 2023-03-10 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0010_alter_sessiondetail_end_time_and_more'),
        ('staff_schedule', '0068_remove_ismsschedulecalendarevent_personal_training_event_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ismsschedulecalendarevent',
            name='personal_training_event',
            field=models.ManyToManyField(blank=True, through='staff_schedule.TrainingSessionInfo', to='trainer.trainersession'),
        ),
        migrations.AddField(
            model_name='trainingsessioninfo',
            name='calendar_Event',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='staff_schedule.ismsschedulecalendarevent'),
            preserve_default=False,
        ),
    ]
