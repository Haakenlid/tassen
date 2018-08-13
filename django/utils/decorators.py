# forked from https://github.com/peterbe/django-cache-memoize
import hashlib
import inspect
import logging
from functools import wraps

from django.core.cache import cache
from django.utils.encoding import force_bytes, force_text

logger = logging.getLogger('apps')


def ismethod(func):
    return next(iter(inspect.signature(func).parameters.keys()),
                None) == 'self'


def func_rewrite(*args):
    return args


def method_rewrite(self, *args):
    try:
        return [f'{self.pk}{self.modified}', *args]
    except AttributeError:
        return [self, *args]


def cache_memoize(
    timeout=24 * 60 * 60,
    prefix=None,
    args_rewrite=None,
    hit_callable=None,
    miss_callable=None,
    store_result=True,
):
    """Decorator for memoizing function calls where we use the
    "local cache" to store the result.

    :arg int time: Number of seconds to store the result if not None
    :arg string prefix: If None becomes the function name.
    :arg function args_rewrite: Callable that rewrites the args first useful
    if your function needs nontrivial types but you know a simple way to
    re-represent them for the sake of the cache key.
    :arg function hit_callable: Gets executed if key was in cache.
    :arg function miss_callable: Gets executed if key was *not* in cache.
    :arg bool store_result: If you know the result is not important, just
    that the cache blocked it from running repeatedly, set this to False.

    Usage::

        @cache_memoize(
            300,  # 5 min
            args_rewrite=lambda user: user.email,
            hit_callable=lambda: print("Cache hit!"),
            miss_callable=lambda: print("Cache miss :("),
        )
        def hash_user_email(user):
            dk = hashlib.pbkdf2_hmac('sha256', user.email, b'salt', 100000)
            return binascii.hexlify(dk)

    Or, when you don't actually need the result, useful if you know it's not
    valuable to store the execution result::

        @cache_memoize(
            300,  # 5 min
            store_result=False,
        )
        def send_email(email):
            somelib.send(email, subject="You rock!", ...)

    Also, whatever you do where things get cached, you can undo that.
    For example::

        @cache_memoize(100)
        def callmeonce(arg1):
            print(arg1)

        callmeonce('peter')  # will print 'peter'
        callmeonce('peter')  # nothing printed
        callmeonce.invalidate('peter')
        callmeonce('peter')  # will print 'peter'

    Suppose you know for good reason you want to bypass the cache and
    really let the decorator let you through you can set one extra
    keyword argument called `_refresh`. For example::

        @cache_memoize(100)
        def callmeonce(arg1):
            print(arg1)

        callmeonce('peter')                 # will print 'peter'
        callmeonce('peter')                 # nothing printed
        callmeonce('peter', _refresh=True)  # will print 'peter'

    """

    def decorator(func):
        rewrite = args_rewrite
        if rewrite is None:
            if ismethod(func):
                rewrite = method_rewrite
            else:
                rewrite = func_rewrite

        def _make_cache_key(*args, **kwargs):
            cache_key = ':'.join([
                force_text(x) for x in rewrite(*args, **kwargs)
            ] + [force_text(f'{k}={v}') for k, v in kwargs.items()])
            return hashlib.md5(
                force_bytes(
                    'cache_memoize' + (prefix or func.__name__) + cache_key
                )
            ).hexdigest()

        @wraps(func)
        def inner(*args, **kwargs):
            refresh = kwargs.pop('_refresh', False)
            cache_key = _make_cache_key(*args, **kwargs)
            sentry = object()
            if refresh:
                result = sentry
            else:
                result = cache.get(cache_key, sentry)
            if result is sentry:
                result = func(*args, **kwargs)
                if not store_result:
                    # Then the result isn't valuable/important to store but
                    # we want to store something. Just to remember that
                    # it has be done.
                    cache.set(cache_key, True, timeout)
                else:
                    cache.set(cache_key, result, timeout)
                if miss_callable:
                    miss_callable(*args, **kwargs)
            elif hit_callable:
                hit_callable(*args, **kwargs)
            return result

        def invalidate(*args, **kwargs):
            cache_key = _make_cache_key(*args, **kwargs)
            cache.delete(cache_key)

        inner.invalidate = invalidate
        return inner

    return decorator
