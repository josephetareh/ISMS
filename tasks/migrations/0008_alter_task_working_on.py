# Generated by Django 4.1.5 on 2023-02-06 19:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0007_alter_subtask_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='working_on',
            field=models.ManyToManyField(blank=True, related_name='working_on', to=settings.AUTH_USER_MODEL),
        ),
    ]
