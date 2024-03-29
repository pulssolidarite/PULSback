# Generated by Django 3.0.3 on 2022-10-13 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_game_featured'),
        ('fleet', '0015_auto_20221013_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='can_edit_donation_amount',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='featured_campaign',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet.Campaign'),
        ),
        migrations.AddField(
            model_name='customer',
            name='featured_game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.Game'),
        ),
    ]
