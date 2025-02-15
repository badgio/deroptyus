# Generated by Django 3.1.2 on 2020-12-06 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RedeemedCounters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(editable=False, max_length=255, unique=True)),
                ('app_key', models.CharField(max_length=255)),
                ('last_counter', models.IntegerField(default=-1)),
            ],
        ),
    ]
