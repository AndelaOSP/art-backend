# Generated by Django 2.0.1 on 2018-08-10 11:56

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations, models
import django.db.models.deletion


User = get_user_model()

def populate_asset_assignee(apps, schema_editor):
    for user in User.objects.all():
        user.save()

    Department = apps.get_model('core', 'Department')

    for department in Department.objects.all():
        department.save()

    OfficeWorkspace = apps.get_model('core', 'OfficeWorkspace')

    for workspace in OfficeWorkspace.objects.all():
        workspace.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetAssignee',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.Department')),
                ('user', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
                ('workspace', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.OfficeWorkspace')),
            ],
        ),
        migrations.RunPython(populate_asset_assignee),
    ]
