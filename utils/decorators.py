from functools import wraps


def counted(fn):
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)

    wrapper.called = 0
    wrapper.__name__ = fn.__name__
    return wrapper


def cached(f):
    _cache = {}

    @wraps(f)
    def _decorator(args):
        args = tuple(args)
        if args not in _cache:
            _cache[args] = f(args)
        return _cache[args]

    return _decorator
