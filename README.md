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

3. Add a setting to define the user model:

```python
DRF_REQUEST_LOGGING = {
	'USER_MODEL': "example_app.User"
}
```

4. Run migrations:

```sh
manage.py makemigrations
manage.py migrate
```

## TODO

1. Figure out how to do migratiosn with a dynamic field in the app.
