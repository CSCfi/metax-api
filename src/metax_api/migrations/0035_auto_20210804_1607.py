# Generated by Django 3.1.12 on 2021-08-04 13:07

from django.db import migrations, models
import metax_api.utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0034_apierror'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedObject',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=200, unique=True)),
                ('model_name', models.CharField(max_length=200)),
                ('object_data', models.JSONField()),
                ('date_deleted', models.DateTimeField(default=metax_api.utils.utils.get_tz_aware_now_without_micros)),
            ],
        ),
        migrations.AlterField(
            model_name='apierror',
            name='date_created',
            field=models.DateTimeField(default=metax_api.utils.utils.get_tz_aware_now_without_micros),
        ),
    ]