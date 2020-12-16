# Generated by Django 3.1.2 on 2020-12-16 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='image',
            field=models.ImageField(null=True, upload_to='upload/rewards/'),
        ),
        migrations.AddField(
            model_name='reward',
            name='name',
            field=models.CharField(default='Placeholder', max_length=255),
            preserve_default=False,
        ),
    ]
