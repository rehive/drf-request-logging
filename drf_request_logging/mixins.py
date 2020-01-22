import pickle

from django.db import IntegrityError

from .models import Request
from .exceptions import IdempotentRequestExistsError


MASKED_HEADER_KEYS = [
    'HTTP_COOKIE',
    'HTTP_X_CSRFTOKEN',
    'HTTP_AUTHORIZATION',
]

MASKED_BODY_KEYS = [
    "password",
    "password1",
    "password2",
    "old_password",
    "new_password1",
    "new_password2",
    "token",
    "uid",
    "key",
    "otp",
    "secret",
    "csrfmiddlewaretoken",
]


class RequestMixin(object):
    """
    Store each request and handle idempotency behaviour on requests/responses.
    """

    id_key = None
    new_request = None
    old_request = None

    def get_headers(self, meta):
        """
        Get the request headers with sensitive values masked.
        """

        def _mask_and_clean(k, v):
            value = "****" if k in MASKED_HEADER_KEYS else v
            return (k.replace('HTTP_', ''), value)

        return dict(_mask_and_clean(k, v) for k, v in meta.items()
            if ("HTTP_" in k or "CONTENT" in k))

    def get_body(self, data):
        """
        Get the request body with sensitive values masked.
        """

        def _mask(k, v):
            return "****" if k in MASKED_BODY_KEYS else v

        def _clean(data, new_data=None):
            """
            Clean the request body. This also ensures that only safe JSON
            data gets returned.
            """

            try:
                iterator = data.items()
                data_type = 'dict'
                new_data = {} if new_data is None else new_data

            except AttributeError:
                iterator = enumerate(data)
                data_type = 'list'
                new_data = [] if new_data is None else new_data

            for k, v in iterator:
                if isinstance(v, dict) or isinstance(v, list):
                    if data_type == "dict":
                        new_data[k] = _clean(v)
                    elif data_type == "list":
                        new_data.append(_clean(v))

                elif (isinstance(v, int) or isinstance(v, str)
                        or isinstance(v, bool)):
                    if data_type == "dict":
                        new_data[k] = _mask(k, v)
                    elif data_type == "list":
                        new_data.append(_mask(k, v))

                else:
                    if data_type == "dict":
                        new_data[k] = _mask(k, str(v))
                    elif data_type == "list":
                        new_data.append(_mask(k, str(v)))

            return new_data

        return _clean(data)

    def get_idempotency_key(self, user, request):
        """
        Get the idmepotency key sent in the request.
        """

        # Must have a user and be POST/PUT/PATCH.
        if (not user and request.method not in ("POST", "PUT", "PATCH",)):
            return None

        try:
            return request.META['HTTP_IDEMPOTENCY_KEY']
        except KeyError:
            return None

    def initial(self, request, *args, **kwargs):
        """
        Check if request is idempotent and then find an existing saved request
        in the database. If there is an existing saved request then trigger an
        exception.
        """

        super().initial(request, *args, **kwargs)

        user = request.user if not request.user.is_anonymous else None
        self.id_key = self.get_idempotency_key(user, request)

        try:
            self.new_request = Request.objects.create(
                user=user,
                key=self.id_key,
                scheme=request.scheme,
                path=request.path,
                method=request.method,
                encoding=request.encoding,
                content_type=request.content_type,
                params=request.GET,
                headers=self.get_headers(request.META),
                body=self.get_body(request.data),
            )
        except IntegrityError as exc:
            self.old_request = Request.objects.get(
                key=self.id_key,
                user=user
            )
            raise IdempotentRequestExistsError()

    def handle_exception(self, exc):
        """
        Check if an exception is due to an existing idempotent request and if
        it is then immediately return the saved response.
        """

        if isinstance(exc, IdempotentRequestExistsError):
            if (self.id_key and self.old_request
                    and self.old_request.response):
                return pickle.loads(self.old_request.response)

        return super().handle_exception(exc)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Save the request to the database. If it is not a new idempotent request
        update the old one to indicate it was "re-requested".
        """

        response = super().finalize_response(request, response, *args, **kwargs)

        if self.old_request:
            # Update the "updated" date on the request.
            self.old_request.save()
        elif self.new_request:
            # Recheck if a user was set (for auth requests).
            user = request.user if not request.user.is_anonymous else None
            # Add new information about the request.
            self.new_request.user = user
            self.new_request.status_code = response.status_code
            # TODO : Look into saving this as rendered data/text.
            # Pickle messes with the deepcopy functionality on models.
            self.new_request.response = pickle.dumps(response.render())
            self.new_request.save()

        return response
