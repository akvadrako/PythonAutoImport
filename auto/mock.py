"""Simple Mocking"""

from auto.core import Call, indent
from collections import defaultdict

class Mock:
    """A simple mock object."""
    def __init__(self, **attrs):
        self._attrs = defaultdict(Mock)
        self._attrs.update(attrs)

        self._returns = defaultdict(Mock)
        self._calls = []

    def __call__(self, *args, **kw):
        c = Call(*args, **kw)
        self._calls.append(c)

        return self._returns[c]

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        
        return self._attrs[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        else:
            self._attrs[name] = value

    def __repr__(self):
        return 'Mock<0x%0x>' % id(self)

    def __str__(self):
        return '\n'.join(
            [repr(self)] +
            [indent('%s = %s' % kv) for kv in self._attrs.items()]
            )

def test_mock():
    m = Mock()
    m.b.c
    m.b(1,2)

    assert 'c' in m._attrs['b']._attrs
    assert m._attrs['b']._calls == [
        Call(1,2)
    ]