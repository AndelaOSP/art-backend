# -*- coding: UTF-8 -*-
from argparse import RawDescriptionHelpFormatter, FileType
from django.core.management.base import BaseCommand

from core.management.commands import COMMAND_VERSION, DJANGO_VERSION

SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3


class Command(BaseCommand):

    requires_system_checks=True
    requires_migrations_checks=True

    missing_args_message = """
        Specify the path/url to local/remote csv file containing the \
        asset data you want to import
        """


    def get_version(self):
        """Return version (semver) of import_assets command
        """
        return f'import_assets v{COMMAND_VERSION}, Django v{DJANGO_VERSION}'


    def add_arguments(self, parser):
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.description="""
        ------------------------------------------------------------------------
        Command to import Assets from csv file for Andela Resource Tracker (ART)
        ------------------------------------------------------------------------

        Expected inputs:
        - A valid csv file. Eg. '/path/to/file/asset.csv'
        - A URL pointing to a valid csv. Eg. 'http://link-to-csv.com/asset.csv'¹

        Expected columns in input csv file:
            - 'Category'² (required)
            - 'Sub-Category'² (required)
            - 'Type'² (required)
            - 'Make'² (required)
            - 'Model Number'² (required)
            - 'Asset Code'² (optional, unique)
            - 'Serial No.'² (optional, unique)
            - 'Assigned To'² (optional)
            - 'Status'² (optional)
            - 'Memory'² (optional)
            - 'Verified'² (optional)
            - 'Storage'² (optional)
            - 'Processor Type'² (optional)
            - 'YOM'² (optional)
            - 'Notes'² (optional)

        *
          ¹ Coming soon.
          ² without single quotation mark ''.

        Note: Import only supports csv file format.
        """

        parser.add_argument(
            'filepath_or_url',
            nargs=1,
            help=Command.missing_args_message,
            type=FileType('r')
        )

        def handle(self, *args, **options):
            filepath = options['filepath_or_url']
