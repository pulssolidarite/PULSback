# Generated by Django 3.0.3 on 2021-05-19 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0011_delete_donationstep'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('photo', models.FileField(blank=True, null=True, upload_to='campaigns/actions/')),
                ('text', models.TextField(blank=True, null=True)),
                ('campaign', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='donationSteps', to='fleet.Campaign')),
            ],
        ),
    ]
