# Generated by Django 4.1.5 on 2023-03-08 06:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trainer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienttrainerrelationship',
            name='trainer',
            field=models.ForeignKey(blank=True, limit_choices_to={'groups__name': 'Trainer'}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
