from django.contrib import admin
from .models import AssetMake
from .models import AssetCategory, AssetType

admin.site.register(AssetType)
admin.site.register(AssetCategory)
admin.site.register(AssetMake)
