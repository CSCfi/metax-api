# Generated by Django 2.1.11 on 2019-10-18 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0010_auto_20190627_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogrecord',
            name='preservation_dataset_version',
            field=models.OneToOneField(help_text='Link between a PAS-stored dataset and the originating dataset.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='preservation_dataset_origin_version', to='metax_api.CatalogRecord'),
        ),
    ]