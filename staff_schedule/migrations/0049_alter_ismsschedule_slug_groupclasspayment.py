# Generated by Django 4.1.5 on 2023-02-24 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff_schedule', '0048_remove_groupclass_attendees_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismsschedule',
            name='slug',
            field=models.SlugField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='GroupClassPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendees', models.PositiveIntegerField(default=0)),
                ('total_payment', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_for_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff_schedule.groupclass')),
            ],
        ),
    ]
