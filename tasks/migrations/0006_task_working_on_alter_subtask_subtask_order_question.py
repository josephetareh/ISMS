# Generated by Django 4.1.5 on 2023-01-31 18:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0005_alter_subtask_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='working_on',
            field=models.ManyToManyField(blank=True, null=True, related_name='working_on', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subtask',
            name='subtask_order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('subtask', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.subtask')),
            ],
        ),
    ]
