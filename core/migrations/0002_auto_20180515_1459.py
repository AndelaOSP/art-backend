# Generated by Django 2.0.1 on 2018-05-15 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_condition', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Asset Condition',
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='asset_condition',
            field=models.CharField(default='Brand New', editable=False, max_length=50),
        ),
        migrations.AddField(
            model_name='assetcondition',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Asset', to_field='serial_number'),
        ),
    ]
