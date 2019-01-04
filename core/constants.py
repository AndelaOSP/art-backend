from datetime import datetime

AVAILABLE = "Available"
ALLOCATED = "Allocated"
LOST = "Lost"
DAMAGED = "Damaged"

ASSET_STATUSES = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (LOST, "Lost"),
    (DAMAGED, "Damaged")
)

CHECKIN = "Checkin"
CHECKOUT = "Checkout"

ASSET_LOG_CHOICES = (
    (CHECKIN, "Checkin"),
    (CHECKOUT, "Checkout"),
)

LOSS = 'Loss'
DAMAGE = 'Damage'

INCIDENT_TYPES = (
    (LOSS, 'Loss'),
    (DAMAGE, 'Damage')
)

PROCESSOR_TYPE = (
    ("Intel core i3", "Intel core i3"),
    ("Intel core i5", "Intel core i5"),
    ("Intel core i7", "Intel core i7"),
)

PROCESSOR_SPEED = (
    (1.8, "1.8GHz"),
    (2.3, "2.3GHz"),
    (3.0, "3.0GHz"),
    (3.4, "3.4GHz")
)

SCREEN_SIZES = (
    (13, "13\""),
    (15, "15\""),
    (17, "17\"")
)

MEMORY = (
    (4, "4GB"),
    (8, "8GB"),
    (16, "16GB"),
    (32, "32GB")
)

STORAGE_SIZES = (
    (128, "128GB"),
    (256, "256GB"),
    (512, "512GB")
)
YEAR_CHOICES = []
for year in range(2013, (datetime.now().year + 1)):
    YEAR_CHOICES.append((year, year))
