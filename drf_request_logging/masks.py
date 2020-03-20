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

MASKED_RESPONSE_KEYS = [
    "token",
    "key",
    "otp",
    "secret"
]

MASK = "*****"


def mask_and_clean(data, masked_keys):
    def _mask(k, v):
        return MASK if k in masked_keys else v

    def _clean(data, new_data=None):
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


def mask_and_clean_headers(meta):
    return mask_and_clean(
        {k:v for k, v in meta.items() if ("HTTP_" in k or "CONTENT" in k)},
        MASKED_HEADER_KEYS
    )


def mask_and_clean_body(body):
    return mask_and_clean(body, MASKED_BODY_KEYS)


def mask_and_clean_response_data(data):
    return mask_and_clean(data, MASKED_RESPONSE_KEYS)
