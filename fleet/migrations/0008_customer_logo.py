# Generated by Django 3.0.3 on 2022-07-16 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0007_migration_v350_donationsteps'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='logo',
            field=models.FileField(blank=True, null=True, upload_to='customers/logos/'),
        ),
    ]