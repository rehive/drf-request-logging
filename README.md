## Quick start

1. Install the package:

```sh
pip install drf-request-logging
```

2. Add "drf_extra" to your INSTALLED_APPS settings like this:

```python
    INSTALLED_APPS = [
        ...
        'drf_request_logging',
    ]
```

3. Run migrations:

```sh
manage.py migrate
```
