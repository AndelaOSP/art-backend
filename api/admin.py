from django.contrib import admin
from .models import (AssetCategory, AssetType,
                     AssetSubCategory, Item, AssetMake, ItemModelNumber)
admin.register(
    [
        AssetCategory,
        AssetType,
        AssetSubCategory,
        Item,
        AssetMake,
        ItemModelNumber
    ]
)
