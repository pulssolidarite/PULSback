# Generated by Django 3.0.3 on 2022-07-16 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0010_auto_20220716_0954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terminal',
            name='is_free',
        ),
    ]
