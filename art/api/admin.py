from django.contrib import admin
from .models import Asset, CheckinLogs, CheckoutLogs

# Register your models here.
admin.site.register(Asset)
admin.site.register(CheckinLogs)
admin.site.register(CheckoutLogs)

