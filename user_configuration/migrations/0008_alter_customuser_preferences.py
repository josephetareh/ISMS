# Generated by Django 4.1.5 on 2023-02-12 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_configuration', '0007_rename_user_preferences_customuser_preferences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='preferences',
            field=models.JSONField(default=dict, null=True),
        ),
    ]
