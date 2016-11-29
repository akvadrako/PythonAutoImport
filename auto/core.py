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

class Call:
    """An function call argument list formatter."""
    def __init__(self, args, kw):
        self.args = args
        self.kw = kw

    def __str__(self):
        args = [ str(s) for s in self.args ]
        args += [ '%s=%s' % kv for kv in self.kw.items() ]
        return ', '.join(args)

    def __repr__(self):
        return 'Call(%r, %r)' % (self.args, self.kw)