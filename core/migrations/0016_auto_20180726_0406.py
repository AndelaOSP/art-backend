# Generated by Django 2.0.1 on 2018-07-26 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20180724_0951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='asset_condition',
        ),
        migrations.RemoveField(
            model_name='assetcondition',
            name='asset_condition',
        ),
        migrations.AddField(
            model_name='asset',
            name='notes',
            field=models.TextField(default=' ', editable=False),
        ),
        migrations.AddField(
            model_name='assetcondition',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
