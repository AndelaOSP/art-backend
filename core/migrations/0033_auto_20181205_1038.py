# Generated by Django 2.0.1 on 2018-12-05 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_merge_20181102_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='assettype',
            name='has_specs',
            field=models.BooleanField(default=False),
        ),
    ]
