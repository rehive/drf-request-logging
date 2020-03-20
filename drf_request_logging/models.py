import pickle

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from enumfields import EnumField

from drf_request_logging.enums import ResourceType
from drf_request_logging.masks import mask_and_clean_response_data


# Foreign key to the user model, as configured by setting.AUTH_USER_MODEL
# Default: django.contrib.auth.models.User
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

# An enum used to define resource types.
RESOURCE_TYPE = getattr(settings, 'RESOURCE_TYPE', ResourceType)


class Request(models.Model):
    key = models.CharField(db_index=True, null=True, max_length=100)
    # The user who performed the request (the authenticated user).
    # Thie value will be None if no authenticated user is available.
    user = models.ForeignKey(
        USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        # This is required to prevent clashes in projects that already had a
        # request model.
        related_name='drf_requests'
    )
    # Request related information. This data is masked so that passwords and
    # other sensitive information may not be retrieved.
    scheme = models.CharField(max_length=5)
    path = models.CharField(
        db_index=True, null=True, blank=True, max_length=100
    )
    method = models.CharField(db_index=True, max_length=10)
    encoding = models.CharField(null=True, blank=True, max_length=100)
    content_type = models.CharField(max_length=100)
    params = JSONField(null=True, blank=True, default=dict)
    headers = JSONField(null=True, blank=True, default=dict)
    body = JSONField(null=True, blank=True, default=dict)
    status_code = models.IntegerField(db_index=True, null=True, blank=True)
    # The binary response data (pickled).
    response = models.BinaryField(null=True, blank=True)
    # Resource related information. These values will be injected if the
    # following fields are available on the request object:
    #   _resource  (string resource name)
    #   _resource_id (string resource ID)
    # The resource_id will not be set unless a resource is set as well.
    resource = EnumField(
        RESOURCE_TYPE,
        db_index=True,
        null=True,
        blank=True,
        max_length=50,
    )
    resource_id = models.CharField(
        db_index=True, null=True, blank=True, max_length=64
    )
    # Datetime information.
    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('key', 'user')

    def __str__(self):
        return str(self.path)

    @property
    def decoded_response(self):
        response = pickle.loads(self.response)
        return {"data": mask_and_clean_response_data(response.data)}
