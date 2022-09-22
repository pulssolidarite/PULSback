# Generated by Django 3.0.3 on 2022-09-22 13:45

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


def populate_username(apps, schema_editor):
    CustomerModel = apps.get_model('fleet', 'Customer')
    for customer_object in CustomerModel.objects.all():
        customer_object.username = customer_object.company + "_login"
        customer_object.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('fleet', '0010_campaign_squared_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterModelManagers(
            name='customer',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='customer',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this customer belongs to. A customer will get all permissions granted to each of their groups.', related_name='customer_set', related_query_name='customer', to='auth.Group', verbose_name='Groups de permissions'),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='customer',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$180000$4mW6zdYdaz5k$1HZAMW6Cbs7RV5G0BsfkzZ8jyuecI0Lcwvr8nsw50As=', max_length=128, verbose_name='password'), # This default password is the hash for 'default_password'
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this customer.', related_name='customer_set', related_query_name='customer', to='auth.Permission', verbose_name="Permissions d'utilisateur"),
        ),
        migrations.AlterField(
            model_name='customer',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),

        # Add field username as non unique and provide one off default value, same for all rows

        migrations.AddField(
            model_name='customer',
            name='username',
            field=models.CharField(
                default='default_username',
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=150,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name='username',
            ),
            preserve_default=False,
        ),

        # Run python to populate username value with different values for each rows

        migrations.RunPython(populate_username, reverse_code=migrations.RunPython.noop),

        # Alter field username to set it as unique

        migrations.AlterField(
            model_name='customer',
            name='username',
            field=models.CharField(
                default='default_username',
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=150,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name='username',
                unique=True, # Set as unique
            ),
            preserve_default=False,
        ),
    ]
