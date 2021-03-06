# Generated by Django 2.0.1 on 2018-05-15 08:31

import core.models.user
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import oauth2_provider.generators
import oauth2_provider.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('cohort', models.IntegerField(blank=True, null=True)),
                ('slack_handle', models.CharField(blank=True, max_length=50, null=True)),
                ('picture', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'verbose_name_plural': 'All Users',
            },
            managers=[
                ('objects', core.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AllocationHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Allocation History',
            },
        ),
        migrations.CreateModel(
            name='APIUser',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('client_id', models.CharField(db_index=True, default=oauth2_provider.generators.generate_client_id, max_length=100, unique=True)),
                ('redirect_uris', models.TextField(blank=True, help_text='Allowed URIs list, space separated', validators=[oauth2_provider.validators.validate_uris])),
                ('client_secret', models.CharField(blank=True, db_index=True, default=oauth2_provider.generators.generate_client_secret, max_length=255)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('skip_authorization', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('client_type', models.CharField(choices=[('confidential', 'Confidential'), ('public', 'Public')], default='confidential', max_length=32)),
                ('authorization_grant_type', models.CharField(choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials')], default='client-credentials', max_length=32)),
            ],
            options={
                'verbose_name': 'API User',
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_code', models.CharField(max_length=50, unique=True)),
                ('serial_number', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('current_status', models.CharField(editable=False, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Asset Categories',
            },
        ),
        migrations.CreateModel(
            name='AssetLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(choices=[('Checkin', 'Checkin'), ('Checkout', 'Checkout')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Asset', to_field='serial_number')),
            ],
            options={
                'verbose_name': 'Asset Log',
            },
        ),
        migrations.CreateModel(
            name='AssetMake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make_label', models.CharField(max_length=40, verbose_name='Asset Make')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Asset Make',
            },
        ),
        migrations.CreateModel(
            name='AssetModelNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_number', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('make_label', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.AssetMake', verbose_name='Asset Make')),
            ],
            options={
                'verbose_name': 'Asset Model Number',
            },
        ),
        migrations.CreateModel(
            name='AssetStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_status', models.CharField(choices=[('Available', 'Available'), ('Allocated', 'Allocated'), ('Lost', 'Lost'), ('Damaged', 'Damaged')], max_length=50)),
                ('previous_status', models.CharField(blank=True, choices=[('Available', 'Available'), ('Allocated', 'Allocated'), ('Lost', 'Lost'), ('Damaged', 'Damaged')], editable=False, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Asset', to_field='serial_number')),
            ],
            options={
                'verbose_name_plural': 'Asset Statuses',
            },
        ),
        migrations.CreateModel(
            name='AssetSubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_category_name', models.CharField(max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('asset_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.AssetCategory')),
            ],
            options={
                'verbose_name_plural': 'Asset SubCategories',
            },
        ),
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('asset_sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.AssetSubCategory')),
            ],
            options={
                'verbose_name': 'Asset Type',
            },
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('report_type', models.CharField(choices=[('feedback', 'feedback'), ('bug', 'bug')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'User Feedback',
            },
        ),
        migrations.CreateModel(
            name='SecurityUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('badge_number', models.CharField(max_length=30, unique=True)),
            ],
            options={
                'verbose_name': 'Security User',
            },
            bases=('core.user',),
            managers=[
                ('objects', core.models.user.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='reported_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetmake',
            name='asset_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.AssetType'),
        ),
        migrations.AddField(
            model_name='asset',
            name='assigned_to',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='asset',
            name='model_number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.AssetModelNumber'),
        ),
        migrations.AddField(
            model_name='apiuser',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_apiuser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Asset', to_field='serial_number'),
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='current_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_owner_asset', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='allocationhistory',
            name='previous_owner',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='previous_owner_asset', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='assetlog',
            name='checked_by',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='core.SecurityUser'),
        ),
    ]
