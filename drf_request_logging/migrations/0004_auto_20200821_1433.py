# Generated by Django 3.0.5 on 2020-08-21 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_request_logging', '0003_auto_20200304_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='resource_id',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
    ]
