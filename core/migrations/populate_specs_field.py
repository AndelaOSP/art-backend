from django.db import migrations, models


def add_default_spec_value(apps, schema_editor):
    Asset_Type = apps.get_model('core', 'AssetType')
    specs = False
    for asset_type in Asset_Type.objects.all():
        asset_type.has_specs = specs
        asset_type.save()


class Migration(migrations.Migration):
    
    dependencies = [
        ('core', '0001_auto_20181130_1125'),
    ]

    operations = [
        migrations.RunPython(add_default_spec_value),
    ]