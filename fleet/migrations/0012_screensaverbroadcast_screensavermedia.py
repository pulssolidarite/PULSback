# Generated by Django 3.0.3 on 2022-09-20 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0011_auto_20220919_1952'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScreensaverMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('scope', models.CharField(choices=[('public', 'Publique'), ('private', 'Privée')], default='private', help_text='Public : Tous les clients ont accès à ce média. Privée : Vous devez créer des diffusions pour diffuser le média chez des clients spécifiques.', max_length=7)),
                ('youtube_video_id', models.CharField(max_length=255, verbose_name='Id de la vidéo youtube')),
                ('owner', models.ForeignKey(help_text="Seul le propriétaire de ce média peut l'éditer ou le supprimer", on_delete=django.db.models.deletion.CASCADE, related_name='owned_screensave_medias', to=settings.AUTH_USER_MODEL, verbose_name='Propriétaire')),
            ],
            options={
                'verbose_name': "Média d'écran de veille",
                'verbose_name_plural': "Médias d'écran de veille",
            },
        ),
        migrations.CreateModel(
            name='ScreensaverBroadcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visible', models.BooleanField(default=False, verbose_name='Visible')),
                ('terminal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screensaver_broadcasts', to='terminal.Terminal', verbose_name='Terminal')),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screensaver_broadcasts', to='fleet.ScreensaverMedia', verbose_name='Média')),
            ],
            options={
                'verbose_name': "Diffusion d'écran de veille",
                'verbose_name_plural': "Diffusions d'écran de veille",
            },
        ),
    ]
