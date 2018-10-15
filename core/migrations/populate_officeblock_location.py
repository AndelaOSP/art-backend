from django.db import migrations


def update_officeblocks_location(apps, schema_editor):
    office_block = apps.get_model('core', 'OfficeBlock')
    andela_centres = apps.get_model('core', 'AndelaCentre')
    block_location = None
    for office_block in office_block.objects.all():
        # find kenya centre
        centre = andela_centres.objects.filter(country="Kenya")[0]
        if centre:
            block_location = centre
        else:
            andela_centres.objects.create(centre_name="Dojo", country="Kenya")
            block_location = andela_centres.objects.filter(country="Kenya")[0]
        office_block.location = block_location
        office_block.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0031_auto_20181015_1424'),
    ]
    operations = [
        migrations.RunPython(update_officeblocks_location),
    ]
