# Generated by Django 2.1.2 on 2019-01-03 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_andelacentre_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='andelacentre',
            name='country_old',
        ),
    ]
