# Generated by Django 3.0.3 on 2020-09-30 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_remove_game_file2'),
    ]

    operations = [
        migrations.AddField(
            model_name='core',
            name='bios_path',
            field=models.CharField(default='bios', max_length=255),
            preserve_default=False,
        ),
    ]