# Generated by Django 3.1.2 on 2020-11-30 14:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0002_auto_20201130_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='badge',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 30, 14, 19, 15, 57657)),
        ),
    ]
