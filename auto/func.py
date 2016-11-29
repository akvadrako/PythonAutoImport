"""
Function-related utilities
"""

from auto.core import Call

########################################## misc

def copy_func(f, name=None, _globals=None):
    """Copy a function."""
    import types
    return types.FunctionType(
        f.__code__,
        f.__globals__ if _globals is None else _globals,
        name or f.__name__,
        f.__defaults__,
        f.__closure__,
    )

########################################## partials

class Partial:
    """A function call and arguments."""
    def __init__(self, func, args, kw):
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self):
        return self.func(*self.args, **self.kw)

    def __str__(self):
        return '%s(%s)' % (self.func.__name__, Call(self.args, self.kw))

########################################## decorators

def wrapper(_wrapper):
    """Transform a function into a decorator.

    wrapper(foo)(bar)(x,y) -> lambda x, y: foo(Partial(bar, [x,y]))
    """
    from functools import wraps

    @wraps(_wrapper)
    def decorator(inner):

        @wraps(inner)
        def decorated(*args, **kw):
            partial = Partial(inner, args, kw)
            return _wrapper(partial)

        decorated._wrapper = inner
        return decorated

    decorator._wrapped = _wrapper
    return decorator

################################################# trace

@wrapper
def trace(partial):
    """Tracing function wrapper."""
    from logging import getLogger

    log = getLogger('trace')

    try:
        ret = partial()
        log.info('%s -> %s', partial, ret)
        return ret
    except Exception as e:
        log.warn('%s throws %s', partial, e.__class__)
        raise

from auto.core import Call
from auto.mock import Mock

def test_trace():
    g = dict(
        Partial=Partial,
        __import__=Mock()
    )
    target = copy_func(trace, _globals=g)

    @target
    def blah(x):
        return x + 1

    assert g['__import__']('logging').getLogger.info._calls == Call()
    assert blah(3) == 4


