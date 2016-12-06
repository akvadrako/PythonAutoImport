"""
Low level code with no dependencies,
that are used by other almost-core code.
"""

########################################

def indent(text):
    """Indent each line of text."""
    lines = str(text).split('\n')
    return '\n'.join('    %s' % l for l in lines)

def test_indent():
    assert indent('a\n b') == '    a\n     b'

########################################

def caller():
    '''Return the calling module + function'''
    import inspect
    frame = inspect.currentframe().f_back.f_back
    mod = inspect.getmodule(frame)
    return "%s:%s" % (mod.__name__, frame.f_lineno)

########################################

class Call:
    """An function call argument list formatter."""
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def __eq__(self, other):
        return self.args == other.args and \
            self.kw == other.kw

    def __hash__(self):
        if self.args:
            return hash(self.args)
        else:
            return hash(self.kw)

    def __str__(self):
        args = [ str(s) for s in self.args ]
        args += [ '%s=%s' % kv for kv in self.kw.items() ]
        return '(%s)' % ', '.join(args)

    def __repr__(self):
        return 'Call%s' % self

########################################

class Globals:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

