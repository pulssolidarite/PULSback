# Generated by Django 3.0.3 on 2020-10-03 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0003_auto_20200929_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal',
            name='play_timer',
            field=models.BigIntegerField(default=10),
        ),
    ]
