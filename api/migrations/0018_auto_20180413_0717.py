# Generated by Django 2.0.1 on 2018-04-13 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20180413_0404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_code',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='serial_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
