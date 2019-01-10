# App Imports
from core.management.commands.import_assets import (create_object, read_csv_row_value, SKIPPED_ROWS,
                                                    write_skipped_records)


def save_asset(data, skipped_file):
    for pos, row in enumerate(data):
        row_data = {
            "row": row,
            "row_count": pos,
            "required_for_import": True,
        }
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
            name=type_value, **row_data,
        )

        make_value = read_csv_row_value("Make", row)
        asset_make = create_object(
            "AssetMake",
            parent={"asset_type": asset_type},
            name=make_value,
            **row_data,
        )

        modelnumber_value = read_csv_row_value("Model Number", row)
        asset_model_no = create_object(
            "AssetModelNumber",
            parent={"asset_make": asset_make},
            name=modelnumber_value,
            **row_data,
        )

        assetcode_value = read_csv_row_value("Asset Code", row)
        serialnumber_value = read_csv_row_value("Serial No.", row)

        asset_fields = {
            "asset_code": assetcode_value,
            "serial_number": serialnumber_value,
        }
        asset = create_object(
            "Asset",
            parent={"model_number": asset_model_no},
            **row_data,
            **asset_fields,
        )

        if asset:
            row_data["required_for_import"] = False

            asset_verified_value = read_csv_row_value("Verified", row)
            asset_verified_value = (True, False)[
                asset_verified_value == "No"
            ]
            asset.verified = asset_verified_value
            asset.save()

            assigned_to_email_value = read_csv_row_value("Assigned To", row)
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

            asset_status_value = read_csv_row_value("Status", row)
            if asset_status_value:
                create_object(
                    "AssetStatus",
                    parent={"asset": asset},
                    current_status=asset_status_value,
                    **row_data,
                )

            asset_condition_notes_value = read_csv_row_value("Notes", row)
            if asset_condition_notes_value:
                create_object(
                    "AssetCondition",
                    parent={"asset": asset},
                    notes=asset_condition_notes_value,
                    **row_data,
                )

            spec_memory_value = read_csv_row_value("Memory", row)
            spec_storage_value = read_csv_row_value("Storage", row)
            spec_processor_type_value = read_csv_row_value(
                "Processor Type", row
            )
            spec_year_of_manufacture_value = read_csv_row_value("YOM", row)

            spec_data = (
                spec_memory_value or spec_storage_value or spec_processor_type_value or spec_year_of_manufacture_value
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
                asset.specs = asset_spec
                asset.save()

    write_skipped_records(SKIPPED_ROWS, skipped_file)
    if len(SKIPPED_ROWS) > 0:
        return False
    else:
        return True
