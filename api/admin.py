from django.contrib import admin
from .models import (AssetCategory, AssetType,
                     AssetSubCategory, Item, AssetMake, ItemModelNumber)
admin.site.register(
    [
        AssetCategory,
        AssetType,
        AssetSubCategory,
        Item,
        AssetMake,
        ItemModelNumber
    ]
)
