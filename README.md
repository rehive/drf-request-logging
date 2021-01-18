<p align="center">
  <img width="64" src="https://avatars2.githubusercontent.com/u/22204821?s=200&v=4" alt="Rehive Logo">
  <h1 align="center">DRF Request logging</h1>
  <p align="center">Request logging for Django REST Framework.</p>
</p>


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
