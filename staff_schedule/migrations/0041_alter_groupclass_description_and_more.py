# Generated by Django 4.1.5 on 2023-02-23 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0040_groupclass_trainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupclass',
            name='description',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='description',
            field=models.TextField(max_length=3000),
        ),
    ]
