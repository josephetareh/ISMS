# Generated by Django 4.1.5 on 2023-03-10 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0009_delete_groupclasspayment'),
        ('staff_schedule', '0065_alter_ismsschedulecalendarevent_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismsschedulecalendarevent',
            name='personal_training_event',
            field=models.ManyToManyField(blank=True, to='trainer.trainersession'),
        ),
    ]
