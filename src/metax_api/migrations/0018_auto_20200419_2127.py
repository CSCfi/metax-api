# Generated by Django 2.2.9 on 2020-04-19 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0017_catalogrecord_rems_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogrecord',
            name='files',
            field=models.ManyToManyField(related_query_name='record', to='metax_api.File'),
        ),
    ]
