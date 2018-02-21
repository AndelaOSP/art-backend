from django.db import models


class AssetCategory(models.Model):
    """ Stores all asset categories """
    category_name = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.category_name


class AssetType(models.Model):
    """Stores all asset types"""
    asset_type = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.asset_type
