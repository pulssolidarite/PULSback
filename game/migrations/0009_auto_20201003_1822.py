# Generated by Django 3.0.3 on 2020-10-03 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_auto_20201003_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='btn_select',
            field=models.CharField(blank=True, default='Select', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='btn_start',
            field=models.CharField(blank=True, default='Start', max_length=255, null=True),
        ),
    ]
