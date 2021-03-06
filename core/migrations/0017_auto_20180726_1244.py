# Generated by Django 2.0.1 on 2018-07-26 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20180726_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficeFloor',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('block', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='core.OfficeBlock')),
            ],
            options={
                'verbose_name': 'Office Floor',
                'ordering': ['-id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='officefloor',
            unique_together={('block', 'number')},
        ),
    ]
