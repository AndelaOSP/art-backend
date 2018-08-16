import os

from tableschema import Table, validate, exceptions


BASE_PATH = os.path.dirname(os.path.abspath(__file__))

#  DATA_FILE = os.path.join(
#     BASE_PATH,
#     'assets.csv'
# )
SCHEMA_PATH = os.path.join(
    BASE_PATH,
    'schema.json'
)


def load_data_from_local_csv_file(filepath):
    table = Table(filepath, schema=SCHEMA_PATH)

    import ipdb; ipdb.set_trace()
    try:
        valid = validate(table.schema.descriptor)
        if valid:
            for keyed_row in table.iter(keyed=True):
                yield keyed_row
    except exceptions.ValidationError as exception:
        import ipdb; ipdb.set_trace()


def load_data_from_remote_csv_file(fileurl):
    pass
