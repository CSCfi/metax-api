# Generated by Django 2.2.9 on 2020-02-18 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0014_catalogrecord_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='datacatalog',
            name='catalog_record_services_create',
            field=models.CharField(blank=True, help_text='Services which are allowed to edit catalog records in the catalog.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='datacatalog',
            name='catalog_record_services_edit',
            field=models.CharField(blank=True, help_text='Services which are allowed to edit catalog records in the catalog.', max_length=200, null=True),
        ),
    ]
