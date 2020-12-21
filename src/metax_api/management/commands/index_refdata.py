from django.core.management.base import BaseCommand

from metax_api.tasks.refdata.refdata_indexer.index_data import index_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('------index refdata------')
        index_data()
