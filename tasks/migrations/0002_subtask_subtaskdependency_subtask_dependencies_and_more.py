# Generated by Django 4.1.5 on 2023-01-31 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtask_name', models.CharField(max_length=128)),
                ('status', models.BooleanField(choices=[('FR', 'Fresh Tasks'), ('IPR', 'In Progress Tasks'), ('ESC', 'Escalated Tasks'), ('COMP', 'Complete Tasks'), ('ARCH', 'Archived Tasks')], max_length=4)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('subtask_type', models.CharField(choices=[('FTSK', 'Form Task'), ('UTSK', 'Upload Task'), ('GTSK', 'Generic Task')], default='GTSK', max_length=4)),
                ('subtask_order', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SubTaskDependency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependency_status', models.CharField(choices=[('BLK', 'Blocking'), ('WTN', 'Waiting')], default='BLK', max_length=3)),
                ('from_subtask', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_subtask', to='tasks.subtask')),
                ('to_subtask', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_subtask', to='tasks.subtask')),
            ],
        ),
        migrations.AddField(
            model_name='subtask',
            name='dependencies',
            field=models.ManyToManyField(blank=True, null=True, through='tasks.SubTaskDependency', to='tasks.subtask'),
        ),
        migrations.AddField(
            model_name='subtask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
        migrations.AddConstraint(
            model_name='subtaskdependency',
            constraint=models.UniqueConstraint(fields=('from_subtask', 'to_subtask'), name='unique_subtask_dependency'),
        ),
    ]