# Generated by Django 3.0.3 on 2023-06-06 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0018_auto_20221209_0620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['id'], 'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
    ]
