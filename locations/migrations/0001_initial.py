# Generated by Django 3.1.2 on 2020-12-06 23:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('website', models.CharField(max_length=255, null=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('image', models.ImageField(null=True, upload_to='upload/locations/')),
                ('status', models.CharField(choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('PENDING', 'Pending Approval')], default='PENDING', max_length=255)),
                ('instagram', models.CharField(max_length=255, null=True)),
                ('facebook', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
