# Generated by Django 3.0.3 on 2020-10-03 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0005_remove_campaign_featured_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='maintenance_type',
        ),
    ]
