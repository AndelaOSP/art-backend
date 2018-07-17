# Generated by Django 2.0.1 on 2018-07-17 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_asset_purchase_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetincidentreport',
            name='submitted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='assetspecs',
            unique_together={('storage', 'memory', 'screen_size', 'processor_speed', 'year_of_manufacture', 'processor_type')},
        ),
    ]
