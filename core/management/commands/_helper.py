import os
import tabulator
import avro.schema
from collections import namedtuple
from avro.datafile import DataFileWriter
from avro.io import DatumWriter

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ASSET_SCHEMA = os.path.join(
    BASE_PATH,
    'assets.avsc'
)
SCHEMA_OUT = os.path.join(
    BASE_PATH,
    'assets.avro'
)


def load_data_from_local_csv_file(filepath):
    try:
        with tabulator.Stream(filepath, delimiter=',', headers=1, encoding='utf-8') as stream:
            for row in stream.iter(keyed=True):
                # import ipdb; ipdb.set_trace()
                # print(row)
                yield(row)

            stream.reset()
            # rows = stream.read()
    except tabulator.exceptions.TabulatorException as e:
        pass
    # with open(filepath, 'rU') as csv_data:
    #     csv_data.readline()
    #     reader = csv.reader(csv_data)
    #     for row in reader:
    #         yield row


def load_data_from_remote_csv_file(fileurl):
    pass

def parse_schema(path=ASSET_SCHEMA):
    with open(path, 'r') as data:
        return avro.schema.Parse(data.read())

def serialize_data(records):
    schema = parse_schema()
    with open(SCHEMA_OUT, 'wb') as out:
        writer = DataFileWriter(out, DatumWriter(), schema)
        for record in records:
            import ipdb; ipdb.set_trace()
            # record = namedtuple('AssetRecord', record.keys())(**record)
            # record = dict((f, getattr(record, f)) for f in record._fields)
            writer.append(record)
