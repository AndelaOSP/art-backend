# Generated by Django 2.0.1 on 2018-03-19 13:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180319_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='user_id',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
