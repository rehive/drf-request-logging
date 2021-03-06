# Generated by Django 2.2.2 on 2020-12-19 19:29

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion

from drf_request_logging.models import USER_MODEL


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, null=True)),
                ('scheme', models.CharField(max_length=5)),
                ('path', models.CharField(blank=True, max_length=100, null=True)),
                ('method', models.CharField(max_length=10)),
                ('encoding', models.CharField(blank=True, max_length=100, null=True)),
                ('content_type', models.CharField(max_length=100)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('headers', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('body', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('response', models.BinaryField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='drf_requests', to=USER_MODEL)),
            ],
            options={
                'unique_together': {('key', 'user')},
            },
        ),
    ]