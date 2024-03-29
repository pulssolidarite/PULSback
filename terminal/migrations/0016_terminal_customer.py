# Generated by Django 3.0.3 on 2022-09-22 18:57

from django.db import migrations, models
import django.db.models.deletion

def populate_terminal_customer(apps, schema_editor):
    """
    Move customer from terminal.owner to terminal
    """
    TerminalModel = apps.get_model('terminal', 'Terminal')
    for terminal_object in TerminalModel.objects.all():
        terminal_object.customer = terminal_object.owner.customer
        terminal_object.save()


def reverse_populate_terminal_customer(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0010_campaign_squared_image'),
        ('terminal', '0015_auto_20220723_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal',
            name='customer',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='terminals',
                to='fleet.Customer',
            ),
        ),

        migrations.RunPython(populate_terminal_customer, reverse_populate_terminal_customer),

        migrations.AlterField(
            model_name='terminal',
            name='customer',
            field=models.ForeignKey(
                null=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='terminals',
                to='fleet.Customer',
            ),
        ),
    ]
