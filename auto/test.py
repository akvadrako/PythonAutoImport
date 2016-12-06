"""Testing Utilities."""

from contextlib import contextmanager

@contextmanager
def context():
    yield

########################################

@contextmanager
def patch(target, attr, new=None):
    """Modify a global within this context."""
    if new is None:
        from auto.mock import Mock
        new = Mock()

    old = getattr(target, attr)
    try:
        setattr(target, attr, new)
        yield new
    finally:
        setattr(target, attr, old)
