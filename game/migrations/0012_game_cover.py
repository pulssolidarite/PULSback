# Generated by Django 3.0.3 on 2022-07-16 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20201004_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='cover',
            field=models.FileField(blank=True, null=True, upload_to='games/covers/'),
        ),
    ]
