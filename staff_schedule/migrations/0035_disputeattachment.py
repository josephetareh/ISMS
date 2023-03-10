# Generated by Django 4.1.5 on 2023-02-20 09:33

from django.db import migrations, models
import django.db.models.deletion
import staff_schedule.models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0034_dispute'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisputeAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=280)),
                ('document', models.FileField(null=True, upload_to=staff_schedule.models.dispute_upload_directory_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('dispute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff_schedule.dispute')),
            ],
        ),
    ]
