from django.db import migrations


def update_assets_location(apps, schema_editor):
    Asset = apps.get_model('core', 'Asset')
    andela_locations = apps.get_model('core', 'AndelaCentre')
    center = None
    for asset in Asset.objects.all():
        if andela_locations.objects.filter(country="Kenya")[0]:
            # A Kenyan center exists
            center = andela_locations.objects.filter(country="Kenya")[0]
        else:
            # Create an Andela center in Kenya
            andela_locations.objects.create(centre_name="Dojo", country="Kenya")
            center = andela_locations.objects.filter(country="Kenya")[0]
        asset.asset_location = center
        asset.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20181005_0817'),
    ]

    operations = [
        migrations.RunPython(update_assets_location),
    ]
