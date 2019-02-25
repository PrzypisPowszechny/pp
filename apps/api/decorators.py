from functools import wraps


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
