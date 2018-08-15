import os


BASE_PATH = os.path.dirname(os.path.abspath(__file__))

 DATA_FILE = os.path.join(
    BASE_PATH,
    'assets.csv'
)
SCHEMA_PATH = os.path.join(
    BASE_PATH,
    'schema.json'
)


def load_data_from_local_csv_file(filepath):
    pass


def load_data_from_remote_csv_file(fileurl):
    pass
