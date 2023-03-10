# Generated by Django 4.1.5 on 2023-03-09 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0009_delete_groupclasspayment'),
        ('staff_schedule', '0063_remove_ismsschedulefixedevent_recurring_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='ismsschedulefixedevent',
            name='schedule_type',
            field=models.CharField(choices=[('CS', 'Class'), ('MT', 'Meeting')], max_length=2),
        ),
        migrations.CreateModel(
            name='ISMSScheduleCalendarEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_type', models.CharField(choices=[('MT', 'Meeting'), ('SPE', 'Special Event'), ('PT', 'Personal Training')], max_length=3)),
                ('calendar_dates', models.ManyToManyField(to='staff_schedule.calendarevent')),
                ('meeting_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff_schedule.meeting')),
                ('personal_training_event', models.ManyToManyField(to='trainer.trainersession')),
            ],
        ),
    ]
