# Generated by Django 2.0.1 on 2018-04-13 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20180413_0717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL),
        ),
    ]
