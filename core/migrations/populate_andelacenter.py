from django.db import migrations


def add_user_location(apps, schema_editor):
    User = apps.get_model('core', 'User')
    location = apps.get_model('core', 'AndelaCentre')
    center = None
    for user in User.objects.all():
        if location.objects.filter(country="Kenya").exists():
            # A Kenyan center exists
            center = location.objects.filter(country="Kenya")[0]
        else:
            # Create an Andela center in Kenya
            location.objects.create(centre_name="Dojo", country="Kenya")
            center = location.objects.filter(country="Kenya")[0]
        user.location = center
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_user_location'),
    ]

    operations = [
        migrations.RunPython(add_user_location),
    ]
