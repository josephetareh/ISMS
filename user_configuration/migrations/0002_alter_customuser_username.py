# Generated by Django 4.1.5 on 2023-01-13 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_configuration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=8, unique=True),
        ),
    ]
