# Generated by Django 2.1.7 on 2019-03-28 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_assetincidentreport_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetincidentreport',
            name='state',
        ),
    ]
