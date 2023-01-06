# Generated by Django 3.0.3 on 2023-01-06 06:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0020_auto_20230104_0610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='donator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='terminal.Donator'),
        ),
    ]
