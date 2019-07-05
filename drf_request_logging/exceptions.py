from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from rest_framework import status


class BaseException(Exception):
    """
    Generic exception that handles a status code, default detail and slug.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('A server error occurred.')
    default_error_slug = 'internal_error'

    def __init__(self, detail=None, error_slug=None):
        if detail is not None:
            self.detail = force_text(detail)
            self.error_slug = force_text(error_slug)
        else:
            self.detail = force_text(self.default_detail)
            self.error_slug = force_text(self.default_error_slug)

    def __str__(self):
        return self.detail


class IdempotentRequestExistsError(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Idempotent request exists.')
    default_error_slug = 'idempotency_request_exists_error'
