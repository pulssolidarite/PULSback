# Generated by Django 3.0.3 on 2023-06-06 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_auto_20230606_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='kill_script',
        ),
        migrations.AlterField(
            model_name='game',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Titre'),
        ),
    ]