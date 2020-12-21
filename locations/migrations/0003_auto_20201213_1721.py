# Generated by Django 3.1.2 on 2020-12-13 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_location_manager'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'permissions': (('view_stats', 'Can view statistics for a location'),)},
        ),
        migrations.AddField(
            model_name='location',
            name='totalVisitors',
            field=models.IntegerField(default=0),
        ),
    ]
