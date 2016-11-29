"""Simple Mocking"""

from auto.core import Call, indent

class Mock:
    """A simple mocking class."""
    def __init__(self, name=''):
        self._name = name
        self._parts = dict()
        self._calls = []

    def __call__(self, *args, **kw):
        self._calls.append(Call(args, kw))

    def __getattr__(self, name):
        if not name in self._parts:
            full = (self._name + '.' + name).strip('.')
            self._parts[name] = Mock(full)

        return self._parts[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        else:
            self._parts[name] = value

    def __repr__(self):
        return 'Mock(%r)' % self._name

    def __str__(self):
        print(self._name, list(self._parts.values()))
        return '\n'.join(
            ['Mock(%r)' % self._name] +
            [indent('call(%s)' % c) for c in self._calls] +
            [indent('%s: %s' % kv) for kv in self._parts.items()]
            )

def test_mock():
    m = Mock()
    m.b.c
    m.b(1,2)

    assert str(m) == ''