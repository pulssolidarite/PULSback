# Generated by Django 3.0.3 on 2022-07-16 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0009_campaign_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='squared_image',
            field=models.FileField(blank=True, null=True, upload_to='campaigns/squared_images/'),
        ),
    ]
