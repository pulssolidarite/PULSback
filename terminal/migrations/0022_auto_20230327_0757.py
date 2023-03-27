# Generated by Django 3.0.3 on 2023-03-27 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0018_auto_20221209_0620'),
        ('game', '0014_auto_20230203_1308'),
        ('terminal', '0021_auto_20230106_0633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-date'], 'verbose_name': 'Paiement', 'verbose_name_plural': 'Paiements'},
        ),
        migrations.AddField(
            model_name='terminal',
            name='check_for_updates',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='terminal',
            name='version',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.FloatField(verbose_name='Montant du paiement'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount_donated',
            field=models.FloatField(null=True, verbose_name='Montant reversé pour la campagne'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='fleet.Campaign', verbose_name='Campagne'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.CharField(max_length=255, verbose_name='Monnaie'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='donation_formula',
            field=models.CharField(choices=[('Classique', 'Classique'), ('Gratuit', 'Gratuit'), ('Mécénat', 'Mécénat'), ('Partage', 'Partage')], max_length=250, null=True, verbose_name='Formule de don'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='donator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='terminal.Donator', verbose_name='Donateur'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='game.Game', verbose_name='Jeu'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(max_length=255, verbose_name='Méthode de paiement'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_terminal',
            field=models.CharField(max_length=250, null=True, verbose_name='TPE'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(max_length=255, verbose_name='Status du paiement'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='terminal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='terminal.Terminal', verbose_name='Borne'),
        ),
    ]
