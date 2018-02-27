from django.db import models
from django.core.exceptions import ValidationError


class AssetCategory(models.Model):
    """ Stores all asset categories """
    category_name = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.category_name


class AssetType(models.Model):
    """Stores all asset types"""
    asset_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.asset_type


class AssetMake(models.Model):
    """ stores all asset makes """
    make_label = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.make_label


class Item(models.Model):
    """Stores all items"""
    item_code = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        raise ValidationError(('Please provide either the serial number,\
                               asset code or both.'), code='required')

    def save(self, *args, **kwargs):
        """Validate either item code or serial number are provided"""
        if not self.item_code and not self.serial_number:
            self.full_clean()
        else:
            super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return '{}{}'.format(self.item_code, self.serial_number)
