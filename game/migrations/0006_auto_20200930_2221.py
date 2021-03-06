# Generated by Django 3.0.3 on 2020-09-30 20:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_core_bios_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='core',
            name='bios',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.BiosFile'),
        ),
        migrations.AlterField(
            model_name='core',
            name='bios_path',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
