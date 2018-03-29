# Generated by Django 2.0.1 on 2018-03-22 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_securityuser'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': 'All Users'},
        ),
        migrations.AddField(
            model_name='item',
            name='status',
            field=models.CharField(choices=[
                ('Available', 'Available'),
                ('Allocated', 'Allocated'),
                ('Lost', 'Lost'),
                ('Damaged', 'Damaged')],
                default='Available',
                max_length=9),
        ),
        migrations.AlterField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL),
        ),
    ]