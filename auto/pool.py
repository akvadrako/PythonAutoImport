"""An implementation of a pool of handles."""

from contextlib import contextmanager

@contextmanager
def ignore_errors():
    """Ignore and log errors."""
    try:
        yield
    except Exception as e:
        log.error('%s', e)


class PoolItem:
    """An entry in a pool."""

    def reset(self, item):
        """Override in sub-classes"""
        pass

    def close(self, item):
        """Override in sub-classes"""
        pass


class Pool:
    """A pool of handles.

    factory should return a new PoolItem instance.
    """
    def __init__(self, factory):
        self.factory = factory
        self.idle = []
        self.active = []

    @contextmanager
    def __call__(self):
        try:
            item = self.idle.pop()
        except IndexError:
            item = self.factory()
        
        try:
            self.active.append(item)
            yield item
            item.reset()
        except Exception:
            with ignore_errors():
                item.close()
            
            self.active.remove(item)
            self.idle.append(item)
            raise
