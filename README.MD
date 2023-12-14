# How to use the token bucket rate limiter

a. Install Redis.
b. Set the settings for redis in settings.py.

Bucket size, Refresh rate and Expiration can be set here for token bucket algorithm
for rate limiting

BUCKET_SIZE = 10
REFRESH_RATE = 1 # Seconds
CACHE_TTL = -1  # -1 means that no expiration is set


# Redis settings.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
    }
}

c. Add the middleware to the MIDDLEWARE lists.
d. Install celery.
e. Install django-celery and add it to the app.
f. add environment for django settings in celery.py.

g. Start celery beat and celery workers
celery -A rate_limiter  beat --loglevel=debug
celery -A rate_limiter  worker --loglevel=info