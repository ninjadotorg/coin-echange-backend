import functools
import logging

from django.core.cache import cache
from rest_framework.exceptions import APIException


def raise_api_exception(exception: APIException):
    def handle_exception(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.exception(e)
                raise exception

        return wrapper

    return handle_exception


def cache_first(cache_key: str, timeout: int = None):
    def handle_exception(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args or kwargs:
                data = cache.get(cache_key.format(*args, **kwargs))
            else:
                data = cache.get(cache_key)

            if data:
                return data

            data = func(*args, **kwargs)
            if args or kwargs:
                cache.set(cache_key.format(*args, **kwargs), data, timeout=timeout)
            else:
                cache.set(cache_key, timeout=timeout)

            return data

        return wrapper

    return handle_exception
