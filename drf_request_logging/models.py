from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings


SETTINGS = getattr(settings, 'DRF_REQUEST_LOGGING', {})
USER_MODEL = getattr(SETTINGS, 'USER_MODEL'),


class Request(models.Model):
    key = models.CharField(null=True, max_length=100)
    user = models.ForeignKey(
        USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    scheme = models.CharField(max_length=5)
    path = models.CharField(null=True, blank=True, max_length=100)
    method = models.CharField(max_length=10)
    encoding = models.CharField(null=True, blank=True, max_length=100)
    content_type = models.CharField(max_length=100)
    params = JSONField(null=True, blank=True, default=dict)
    headers = JSONField(null=True, blank=True, default=dict)
    body = JSONField(null=True, blank=True, default=dict)
    status_code = models.IntegerField(null=True, blank=True)
    response = models.BinaryField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('key', 'user')

    def __str__(self):
        return str(self.path)
