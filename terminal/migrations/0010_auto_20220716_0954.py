# Generated by Django 3.0.3 on 2022-07-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0009_terminal_donation_formula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal',
            name='donation_formula',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='free_mode_text',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='payment_terminal',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
