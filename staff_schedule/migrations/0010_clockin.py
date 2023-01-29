# Generated by Django 4.1.5 on 2023-01-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0009_event_event_day'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClockIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_clocked_in', models.DateTimeField()),
                ('status', models.CharField(choices=[('IA', 'Inactive'), ('EA', 'Early'), ('LTE', 'Late'), ('ONS', 'On Shift'), ('DSP', 'Disputing'), ('DSPF', 'Dispute Failed'), ('DSPS', 'Dispute Succeeded')], default='IA', max_length=4)),
            ],
        ),
    ]
