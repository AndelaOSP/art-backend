# Generated by Django 2.0.1 on 2018-03-21 11:48

from django.db import migrations, models


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
            field=models.CharField
            (choices=[('Available', 'Available'),
                      ('Allocated', 'Allocated'),
                      ('Lost', 'Lost'),
                      ('Damaged', 'Damaged')],
             default='Available',
             max_length=9),
        ),
    ]
