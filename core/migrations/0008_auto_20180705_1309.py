# Generated by Django 2.0.1 on 2018-07-05 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20180705_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
