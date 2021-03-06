# Generated by Django 3.0.3 on 2020-09-29 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20200929_2112'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiosFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='games/bios/')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='file2',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rom2', to='game.GameFile'),
        ),
        migrations.AlterField(
            model_name='game',
            name='file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rom', to='game.GameFile'),
        ),
        migrations.AddField(
            model_name='core',
            name='bios',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='game.BiosFile'),
            preserve_default=False,
        ),
    ]
