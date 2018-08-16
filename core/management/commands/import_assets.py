# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from ._helper import load_data_from_local_csv_file


class Command(BaseCommand):
    help = 'Bulk create Assets from local or remote csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        
        import ipdb; ipdb.set_trace()
