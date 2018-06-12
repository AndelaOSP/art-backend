import sys
import os
import csv
from tqdm import tqdm
import django

from helpers import display_inserted, display_skipped

project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.asset import AssetCategory, AssetSubCategory  # noqa
print(os.getcwd())
with open("/Users/nel/code/art-backend/utils/seed/sample_csv/sample.csv", 'r', ) as f:
    file_length = len(f.readlines()) - 1
    f.seek(0)
    skipped = dict()
    inserted_records = []
    data = csv.DictReader(f, delimiter=',')
    print(f.readlines())
