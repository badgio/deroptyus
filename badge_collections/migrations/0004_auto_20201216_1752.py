# Generated by Django 3.1.2 on 2020-12-16 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0002_auto_20201206_2359'),
        ('badge_collections', '0003_auto_20201216_1145'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CollectionBadges',
            new_name='CollectionBadge',
        ),
    ]
