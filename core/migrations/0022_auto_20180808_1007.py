# Generated by Django 2.0.1 on 2018-08-08 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0021_auto_20180807_1000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='allocationhistory',
            old_name='object',
            new_name='current_allocation_object_id',
        ),
        migrations.RemoveField(
            model_name='allocationhistory',
            name='content',
        ),
        migrations.RemoveField(
            model_name='allocationhistory',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='allocationhistory',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='current_status',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='object_id',
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='current_allocation_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='previous_allocation_content_type',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='previous', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='previous_allocation_object_id',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='assetstatus',
            name='current_status',
            field=models.CharField(choices=[('Available', 'Available'), ('Allocated', 'Allocated'), ('Lost', 'Lost'), ('Damaged', 'Damaged')], default='Available', max_length=50),
        ),
    ]
