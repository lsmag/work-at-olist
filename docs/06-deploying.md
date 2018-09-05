Deploying Sparrow
======================

When reading `example.env` there are a few variables that
are only useful for development (DEBUG mode) and others that
are only (or more) for production environments. These are:

- DEBUG: either do not set it or set it to `False`. Just to be sure,
  with sparrow's default settings (production.py), `DEBUG` is already
  overriden to `False`
- DATABASE_URL: ... because we need to access the db
- SECRET_KEY: pick a different one for your production environment,
  and keep it secret (because it's a secret!). You can use the command
  below with the caveat that it only creates an alphanumeric secret:
  
    < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;
    
- ALLOWED_HOSTS: it's not needed when in DEBUG mode but it's
  mandatory to production. Comma-separated list. Make sure it's
  set. See more in https://docs.djangoproject.com/en/2.1/ref/settings/#allowed-hosts
