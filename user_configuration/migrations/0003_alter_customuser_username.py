# Generated by Django 4.1.5 on 2023-01-15 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_configuration', '0002_alter_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
