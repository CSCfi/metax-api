# Generated by Django 2.0 on 2018-11-01 13:24

from django.db import migrations, models


"""
Change file_name and directory_name fields from CharField with max_length to TextField, which has
max length of whatever the db supports.

Literature:
https://unix.stackexchange.com/a/32834
https://stackoverflow.com/questions/265769/maximum-filename-length-in-ntfs-windows-xp-and-windows-vista

It's best if Metax does not make any assumptions in this topic. Metax holds metadata of files,
it does not dictate which filesystem a filestorage should use now, in the future, or in the past.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('metax_api', '0004_auto_20180919_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='directory_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='file',
            name='file_name',
            field=models.TextField(),
        ),
    ]