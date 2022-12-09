# Generated by Django 3.0.3 on 2022-12-09 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0017_auto_20221013_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Can this user log into the Admin space and the Django backoffice', verbose_name='Admin'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this admin has all the permissions in the django backoffice without explicitly assigning them.', verbose_name='Superadmin'),
        ),
    ]
