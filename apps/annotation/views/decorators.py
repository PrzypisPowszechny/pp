from functools import wraps

from lazysignup.decorators import allow_lazy_user


def decorate_conditionally(condition, decorator):
    def decorate(func):
        def wrapped(request, *args, **kwargs):
            if condition(request, *args, **kwargs):
                return decorator(func)(request, *args, **kwargs)
            return func(request, *args, **kwargs)
        return wraps(decorator(func))(wrapped)
    return decorate


def apply_for_anonymous(decorator):
    return decorate_conditionally(lambda request, *a, **k: request.user.is_anonymous, decorator)


def allow_lazy_user_smart(func):
    """
    This is allow_lazy_user decorator but executed when it is really needed: for anonymous users.
    This way DB hits are optimized.
    """
    return apply_for_anonymous(allow_lazy_user)(func)
