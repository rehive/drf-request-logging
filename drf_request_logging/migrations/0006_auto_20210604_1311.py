# Generated by Django 3.1.2 on 2021-06-04 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_request_logging', '0005_auto_20201211_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='path',
            field=models.CharField(blank=True, db_index=True, max_length=256, null=True),
        ),
    ]