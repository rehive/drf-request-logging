import pickle
from copy import deepcopy

from django.db import IntegrityError

from .models import Request
from .exceptions import (
    IdempotentRequestExistsError,
    IdempotencyNotSupportedError
)
from .masks import (
    mask_and_clean_headers,
    mask_and_clean_body,
    mask_and_clean_response_data
)


class RequestMixin(object):
    """
    Store each request and handle idempotency behaviour on requests/responses.
    """

    # Store values related to this request.
    id_key = None
    new_request = None
    old_request = None

    # Configure whether idempotency is supported.
    idempotent = True

    def get_headers(self, meta):
        """
        Get the request headers with sensitive values masked.
        """

        return mask_and_clean_headers(meta)

    def get_body(self, body):
        """
        Get the request body with sensitive values masked.
        """

        return mask_and_clean_body(body)

    def get_response(self, response):
        """
        Get the response body with sensitive values masked.

        Expects a rendered response.
        """
        res = deepcopy(response)
        res.data = mask_and_clean_response_data(res.data)
        return res

    def get_idempotency_key(self, user, request):
        """
        Get the idmepotency key sent in the request.
        """

        # Idempotency is not alowed on anonymous user endpoints.
        if not user:
            idempotency_allowed = False
        # Idempotency is not allowed on non POST, PUT and PATCH methods.
        elif request.method not in ("POST", "PUT", "PATCH",):
            idempotency_allowed = False
        else:
            idempotency_allowed = self.idempotent

        # Check if there is an existing idempotency key.
        try:
            id_key = request.META['HTTP_IDEMPOTENCY_KEY']
        except KeyError:
            id_key = None

        # If an idempotency key is used but idempotency is not allowed then
        # throw an idempotency not suppported error.
        if id_key and not idempotency_allowed:
            raise IdempotencyNotSupportedError()

        return id_key

    def initial(self, request, *args, **kwargs):
        """
        Check if request is idempotent and then find an existing saved request
        in the database. If there is an existing saved request then trigger an
        exception.
        """

        super().initial(request, *args, **kwargs)

        user = request.user if not request.user.is_anonymous else None

        id_key = self.get_idempotency_key(user, request)

        if user:
            # Set the idempotency key if it exists.
            self.id_key = id_key

            # Try log the request, if the id_key is not null and not unique an
            # integrity error will be thrown.
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

        # Recheck if a user was set (for auth requests).
        user = request.user if not request.user.is_anonymous else None

        # This is an old request, resave it to get the new updated date.
        if self.old_request:
            # Update the "updated" date on the request.
            self.old_request.save()
            # Set the idempotent replayed header to true.
            response["Idempotent-Replayed"] = "true"
        # This request belongs to a specific user.
        elif user:
            # This request was not previously saved because it was an
            # anonymouse user request. Populate base request.
            if not self.new_request:
               self.new_request = Request(
                    user=user,
                    scheme=request.scheme,
                    path=request.path,
                    method=request.method,
                    encoding=request.encoding,
                    content_type=request.content_type,
                    params=request.GET,
                    headers=self.get_headers(request.META),
                    body=self.get_body(request.data),
                )
            # Add the resource information if any.
            if getattr(request, "_resource", None):
                self.new_request.resource = request._resource
                self.new_request.resource_id = getattr(
                    request, "_resource_id", None
                )
            # Add new information about the request.
            self.new_request.user = user
            self.new_request.status_code = response.status_code
            # Get a rendered and stored response to save on the database.
            rendered_response = response.render()
            stored_response = self.get_response(rendered_response)
            # TODO : Look into saving this as rendered data/text.
            # Pickle messes with the deepcopy functionality on models.
            self.new_request.response = pickle.dumps(stored_response)
            self.new_request.save()

        return response
