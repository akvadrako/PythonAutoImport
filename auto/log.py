"""Logging.

The python logging subsystem doesn't meet my needs very well,
so I'm going to write my own. It's more structured and flexible,
while not supporting lots of stuff I don't need.
"""

from threading import local
from contextlib import contextmanager
from auto.core import caller, Globals
import sys

############################## Python Logging Adapter

from logging import root, Handler

class AdapterHandler(Handler):
    """Translate logging calls from python's standard `logging' package."""

    def handle(self, record):
        """Handler a standard python logging.Record"""
        code = record.levelname or 'LVL%i' % record.levelno
        log(code, '%s: %s' % (record.name, record.getMessage()),
            caller='%s:%s' % (record.module, record.lineno))

from auto.test import patch
from auto.mock import Mock, Call

def test_adapter():
    import logging, sys

    logger = logging.getLogger('test_adapter')
    logger.handlers = [ AdapterHandler() ]

    # patch the log function
    log_func = Mock()

    with patch(sys.modules[__name__], 'log', log_func):
        logger.warn('msg %s', 'var')

    assert log_func._calls == [
        Call('WARNING', 'test_adapter: msg var', caller='log:39')
    ]

############################## Reusable Classes

class Record:
    def __init__(self, time, code, desc, ctx):
        self.time = time
        self.code = code or 'MSG'
        self.desc = desc
        self.ctx = ctx

    def __repr__(self):
        return 'Record(%r, %r, %r, %r)' % (str(self.time), self.code, self.desc, self.ctx)

    def __str__(self):
        msg = '[' + self.time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 'Z]'
        if self.code:
            msg += ' ' + self.code
        if self.desc:
            msg += ' ' + self.desc
        return msg

class DefaultConfig:
    def handle(self, record):
        msg = str(record)
        if record.ctx:
            msg += ' ' + ' '.join('%s: %r' % kv for kv in sorted(record.ctx.items()))
        sys.stderr.write(msg + '\n')

class CaptureConfig:
    def __init__(self):
        self.logs = []

    def handle(self, record):
        self.logs.append(record)

############################### Global Setup

g = Globals(
    config=DefaultConfig(),
    local=local(),
    )
g.local.stack = []

def config():
    root.handlers = [ AdapterHandler() ]

@contextmanager
def context(**cxt):
    g.local.stack.append(cxt)
    try:
        yield
    finally:
        g.local.stack.pop()

def log(code=None, desc=None, **ctx):
    """Log a record."""
    from datetime import datetime
    from sys import exc_info

    ctx = dict(ctx)
    for entry in reversed(g.local.stack):
        for k, v in entry.items():
            ctx.setdefault(k, v)

    ctx.setdefault('caller', caller())
    if exc_info()[0]:
        ctx.setdefault('exception', exc_info())

    record = Record(datetime.utcnow(), code, desc, ctx)

    g.config.handle(record)

def test_logging():
    from io import StringIO
    from all import Pattern

    import sys, datetime
    utcnow = datetime.datetime(3085, 5, 7)

    buffer = StringIO()
    with patch(sys, 'stderr', buffer), \
        patch(datetime, 'datetime', Mock(utcnow=lambda: utcnow)):
        with context(a=1, b=2):
            log('CODE123', 'msg', b=4, x=8)
    
    assert buffer.getvalue() == Pattern(
        "\[3085-05-07 00:00:00.000Z\] CODE123 msg a: 1 b: 4 caller: 'auto.log:\d+' x: 8"
    )

################################# Log Capture

@contextmanager
def capture():
    old = g.config
    g.config = CaptureConfig()
    try:
        yield g.config.logs
    finally:
        g.config = old

def test_capture():
    with capture() as logs:
        log('E102')

    assert logs[0].code == 'E102'
    assert logs[0].desc is None
    assert len(logs) == 1

