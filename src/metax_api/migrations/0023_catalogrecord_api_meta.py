# Generated by Django 2.2.10 on 2020-06-02 04:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0022_auto_20200528_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogrecord',
            name='api_meta',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, help_text='Saves api related info about the dataset. E.g. api version', null=True),
        ),
    ]
