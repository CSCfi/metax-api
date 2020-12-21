from django.core.management.base import BaseCommand

from metax_api.tasks.refdata.refdata_fetcher.fetch_data import fetch_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('------fetch refdata------')
        fetch_data()
