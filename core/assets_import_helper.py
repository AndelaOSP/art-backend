# Standard Library
import csv
import os
from collections import defaultdict

# Third-Party Imports
from django.apps import apps
from django.conf import settings

# App Imports
from core.models.asset import Asset

SKIPPED_ROWS = []

SKIPPED_ASSETS_FILE = os.path.join(settings.BASE_DIR, "skipped.csv")


def process_file(data, progress=None, skipped_file=None):
    global SKIPPED_ROWS
    SKIPPED_ROWS = []
    file_data = defaultdict(list)
    for row_id, row in enumerate(data):
        row_data = {"row": row, "row_count": row_id}
        try:
            progress.update()
        except Exception:
            pass

        process_model_number(row_data)
        model_number = read_csv_row_value("Model Number", row)
        row_data["Asset Code"] = read_csv_row_value("Asset Code", row)
        row_data["Serial No."] = read_csv_row_value("Serial No.", row)
        row_data["Serial No."] = read_csv_row_value("Serial No.", row)
        row_data["Verified"] = read_csv_row_value("Verified", row)
        row_data["Assigned To"] = read_csv_row_value("Assigned To", row)
        row_data["Status"] = read_csv_row_value("Status", row)
        row_data["Notes"] = read_csv_row_value("Notes", row)
        row_data["Memory"] = read_csv_row_value("Memory", row)
        row_data["Storage"] = read_csv_row_value("Storage", row)
        row_data["Processor Type"] = read_csv_row_value("Processor Type", row)
        row_data["YOM"] = read_csv_row_value("YOM", row)
        file_data[model_number].append(row_data)
    process_asset_data(file_data)
    write_skipped_records(SKIPPED_ROWS, filename=skipped_file)
    if len(SKIPPED_ROWS) > 0:
        return False
    else:
        return True


def process_model_number(row_data):
    row = row_data.get('row')

    category_value = read_csv_row_value("Category", row)
    category = create_object("AssetCategory", name=category_value, **row_data)

    subcategory_value = read_csv_row_value("Sub-Category", row)
    subcategory = create_object(
        "AssetSubCategory",
        parent={"asset_category": category},
        name=subcategory_value,
        **row_data,
    )

    type_value = read_csv_row_value("Type", row)
    asset_type = create_object(
        "AssetType",
        parent={"asset_sub_category": subcategory},
        name=type_value,
        **row_data,
    )

    make_value = read_csv_row_value("Make", row)
    asset_make = create_object(
        "AssetMake", parent={"asset_type": asset_type}, name=make_value, **row_data
    )
    model_number_value = read_csv_row_value("Model Number", row)
    create_object(
        "AssetModelNumber",
        parent={"asset_make": asset_make},
        name=model_number_value,
        **row_data,
    )


def process_asset_data(processed_file_data):  # noqa: C901
    for model_number_value, row_datas in processed_file_data.items():
        collection = apps.get_model("core", 'AssetModelNumber')
        try:
            asset_model_obj = collection.objects.get(name__iexact=model_number_value)
        except Exception:
            asset_model_obj = model_number_value
        for row_data in row_datas:
            assetcode_value = row_data.pop("Asset Code")
            serialnumber_value = row_data.pop("Serial No.")
            asset_verified_value = row_data.pop("Verified")
            assigned_to_email_value = row_data.pop("Assigned To")
            asset_status_value = row_data.pop("Status")
            asset_condition_notes_value = row_data.pop("Notes")
            spec_memory_value = row_data.pop("Memory")
            spec_storage_value = row_data.pop("Storage")
            spec_processor_type_value = row_data.pop("Processor Type")
            spec_year_of_manufacture_value = row_data.pop("YOM")

            asset_fields = {
                "asset_code": assetcode_value,
                "serial_number": serialnumber_value,
            }
            asset = create_object(
                "Asset",
                parent={"model_number": asset_model_obj},
                required_for_import=True,
                **row_data,
                **asset_fields,
            )
            if asset:
                asset_verified_value = (True, False)[asset_verified_value == "No"]
                asset.verified = asset_verified_value
                asset.save()

                if assigned_to_email_value:
                    asset_user = create_object(
                        "User", email=assigned_to_email_value, **row_data
                    )

                    create_object(
                        "AllocationHistory",
                        parent={"asset": asset},
                        current_owner=asset_user.assetassignee,
                        **row_data,
                    )

                if asset_status_value:
                    create_object(
                        "AssetStatus",
                        parent={"asset": asset},
                        current_status=asset_status_value,
                        **row_data,
                    )

                if asset_condition_notes_value:
                    create_object(
                        "AssetCondition",
                        parent={"asset": asset},
                        notes=asset_condition_notes_value,
                        **row_data,
                    )

                spec_data = (
                    spec_memory_value
                    or spec_storage_value
                    or spec_processor_type_value
                    or spec_year_of_manufacture_value
                )

                if spec_data:
                    asset_spec = create_object(
                        "AssetSpecs",
                        memory=spec_memory_value,
                        storage=spec_storage_value,
                        processor_type=spec_processor_type_value,
                        year_of_manufacture=spec_year_of_manufacture_value,
                        **row_data,
                    )
                    if asset_spec:
                        asset.specs = asset_spec
                        asset.save()


def read_csv_row_value(header_name, row):
    value = row.get(header_name)
    if value:
        return value.strip()
    return None


def create_object(
    collection,
    parent=None,
    row=None,
    row_count=None,
    required_for_import=False,
    **values,
):
    obj, success = collection_bootstrap(collection, parent, **values)
    if success:
        return obj
    if required_for_import:
        record_errors(row, row_count, obj)
    return success


def record_errors(row, row_count, object_error):
    global SKIPPED_ROWS
    for line in SKIPPED_ROWS:
        if line.get("Row") == row_count:
            error_as_list = list(line["Error"])
            error_as_list += object_error
            line["Error"] = error_as_list
            return
    row["Error"] = object_error
    row["Row"] = row_count
    SKIPPED_ROWS.append(row)


def write_skipped_records(records, filename=None):
    fieldnames = (
        "Row",
        "Category",
        "Sub-Category",
        "Type",
        "Make",
        "Model Number",
        "Asset Code",
        "Serial No.",
        "Assigned To",
        "Status",
        "Memory",
        "Verified",
        "Storage",
        "Processor Type",
        "YOM",
        "Notes",
        "Error",
    )
    if filename:
        global SKIPPED_ASSETS_FILE
        SKIPPED_ASSETS_FILE = os.path.join(
            settings.BASE_DIR, "skippedassets/{}.csv".format(filename)
        )
    with open(SKIPPED_ASSETS_FILE, "w") as skipped_file:
        writer = csv.DictWriter(skipped_file, delimiter=",", fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            row["Error"] = set(row["Error"])
            if "" in row.keys():
                del (row[""])
            writer.writerow(row)


def collection_bootstrap(collection, parent=None, **fields):
    collection = apps.get_model("core", collection)
    try:
        obj = collection.objects.get(**fields)
    except Exception:
        pass
    else:
        if collection is not Asset:
            return obj, True
    if parent is not None:
        missing_parent = [a for a, b in parent.items() if not b]
        if len(missing_parent) > 0:
            return missing_parent, False
    missing_fields = [a for a, b in fields.items() if not b]

    if missing_fields and collection is not Asset:
        return missing_fields, False

    if collection is Asset and len(missing_fields) > 1:
        return missing_fields, False
    return load_to_db(collection, parent, **fields)


def load_to_db(collection, parent=None, **fields):
    try:
        obj = collection.objects.get(**fields)
        if collection is Asset:
            return (
                ["Asset with similar asset code or serial number already imported"],
                False,
            )
        return obj, True
    except Exception:
        try:
            if parent:
                return collection.objects.create(**fields, **parent), True
            else:
                return collection.objects.create(**fields), True
        except Exception as e:
            return [str(e)], False
    return "error creating {}".format(collection), False


class DictReaderStrip(csv.DictReader):
    @property
    def fieldnames(self):
        if self._fieldnames is None:
            csv.DictReader.fieldnames.fget(self)
            if self._fieldnames is not None:
                self._fieldnames = [name.strip() for name in self._fieldnames if name and name.strip()]
        return self._fieldnames
