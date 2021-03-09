# Generated by Django 3.0.3 on 2020-10-03 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20200930_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='is_video',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='video',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]