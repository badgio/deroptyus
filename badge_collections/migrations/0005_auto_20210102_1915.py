# Generated by Django 3.1.2 on 2021-01-02 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badge_collections', '0004_auto_20201216_1752'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collection',
            options={'permissions': (('check_collection_status', 'Can check completion status of a Collection'), ('view_stats', 'Can view statistics for a Collection'))},
        ),
    ]
