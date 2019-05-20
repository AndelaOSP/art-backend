# Standard Library
from datetime import datetime

FEEDBACK = "feedback"
BUG = "bug"
FEATURE_REQUEST = "feature_request"
REPORT_TYPES = (
    (FEEDBACK, "feedback"),
    (BUG, "bug"),
    (FEATURE_REQUEST, "feature request"),
)

AVAILABLE = "Available"
ALLOCATED = "Allocated"
LOST = "Lost"
DAMAGED = "Damaged"

ASSET_STATUSES = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (LOST, "Lost"),
    (DAMAGED, "Damaged"),
)

CHECKIN = "Checkin"
CHECKOUT = "Checkout"

ASSET_LOG_CHOICES = ((CHECKIN, "Checkin"), (CHECKOUT, "Checkout"))

LOSS = "Loss"
DAMAGE = "Damage"

INCIDENT_TYPES = ((LOSS, "Loss"), (DAMAGE, "Damage"))

PROCESSOR_TYPE = (
    ("Intel core i3", "Intel core i3"),
    ("Intel core i5", "Intel core i5"),
    ("Intel core i7", "Intel core i7"),
)

PROCESSOR_SPEED = ((1.8, "1.8GHz"), (2.3, "2.3GHz"), (3.0, "3.0GHz"), (3.4, "3.4GHz"))

SCREEN_SIZES = ((13, '13"'), (15, '15"'), (17, '17"'))

MEMORY = ((4, "4GB"), (8, "8GB"), (16, "16GB"), (32, "32GB"))

STORAGE_SIZES = ((128, "128GB"), (256, "256GB"), (512, "512GB"))
YEAR_CHOICES = []
for year in range(2013, (datetime.now().year + 1)):
    YEAR_CHOICES.append((year, year))

MAKE = "Make"
TYPE = "Type"
ASSET_CODE = "Asset Code"
CATEGORY = "Category"
SUB_CATEGORY = "Sub-Category"
MODEL_NUMBER = "Model Number"
SERIAL_NUMBER = "Serial No."
ASSIGNED_TO = "Assigned To"
STATUS = "Status"
ASSET_MEMORY = "Memory"
VERIFIED = "Verified"
NOTES = "Notes"
STORAGE = "Storage"
ASSET_PROCESSOR_TYPE = "Processor Type"
YOM = "YOM"
ROW = "Row"
ERROR = "Error"

CSV_HEADERS = {
    MAKE,
    TYPE,
    ASSET_CODE,
    CATEGORY,
    SUB_CATEGORY,
    MODEL_NUMBER,
    SERIAL_NUMBER,
    ASSIGNED_TO,
    STATUS,
    ASSET_MEMORY,
    VERIFIED,
    NOTES,
    STORAGE,
    ASSET_PROCESSOR_TYPE,
    YOM,
    ROW,
    ERROR,
}
CSV_REQUIRED_HEADING = {MODEL_NUMBER}
CSV_REQUIRED_HEADING_ASSET_CODE = CSV_REQUIRED_HEADING.union({ASSET_CODE})
CSV_REQUIRED_HEADING_SERIAL_NO = CSV_REQUIRED_HEADING.union({SERIAL_NUMBER})

NEWLY_REPORTED = "newly reported"
INTERNAL_ASSESSMENT = "internal assessment"
EXTERNAL_ASSESSMENT = "external assessment"
OUT_FOR_REPAIR = "out for repair"

REPORT_STATE_OPTIONS = (
    (NEWLY_REPORTED, "newly reported"),
    (INTERNAL_ASSESSMENT, "internal assessment"),
    (EXTERNAL_ASSESSMENT, "external assessment"),
    (OUT_FOR_REPAIR, "out for repair"),
)


REQUIRES_REPAIR = "requires repair"
REQUIRES_EXTERNAL_ASSESSMENT = "requires external assessment"

ASSET_STATE_FROM_REPORT_OPTIONS = (
    (REQUIRES_REPAIR, "requires repair"),
    (REQUIRES_EXTERNAL_ASSESSMENT, "requires external assessment"),
    (DAMAGED, "Damaged"),
)

PAID = "paid"
POSTPAID = "postpaid"

SIMCARD_ASSET_OPTIONS = ((PAID, "paid"), (POSTPAID, "postpaid"))
