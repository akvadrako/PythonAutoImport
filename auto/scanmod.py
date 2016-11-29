"""Python Module Scanner"""

import logging

from importlib import import_module

from auto.dblite import Schema, Column
from auto.lib import mtime, scan_modules

log = logging.getLogger(__name__)

modules_schema = Schema('modules',
    Column('name', 'TEXT', 'PRIMARY KEY'),
    Column('path', 'TEXT'),
    Column('modified', 'TIMESTAMP'),
)

attrs_schema = Schema('attrs',
    Column('name', 'TEXT', 'PRIMARY KEY'),
    Column('module', 'TEXT'),
    Column('last_used', 'TIMESTAMP'),
)

def init_db(db):
    db.add_table(modules_schema)
    db.add_table(attrs_schema)


def store_attrs(db, modname):
    """Store the attributes in modname."""
    rec = db.get('modules', name=modname)
    if rec:
        # always assume an empty path is up-to-date (maybe builtin?)
        if not rec['path']:
            return
        
        # check if the record needs to be updated
        if mtime(rec['path']) <= rec.modified:
            return

    log.debug('updating attributes for %s', modname)
    db.delete('attrs', module=modname)

    mod = import_module(modname)
    for attr in dir(mod):
        db.insert('attrs',
            name=attr,
            module=modname,
        )

    path = getattr(mod, '__file__', None)

    db.replace('modules',
        name=modname,
        path=path,
        modified=mtime(path) if path else None,
    )

def update(db):
    """Update db."""
    init_db(db)
    for modname in scan_modules():
        store_attrs(db, modname)

def lookup(db, prefix):
    """Return a list of completions for prefix"""
    with db.pool() as conn:
        cursor = conn('SELECT * FROM attrs WHERE name LIKE ?',
            [prefix + '%'])

        return [ (r['module'], r['name']) for r in cursor ]

def test_scanmod():
    from auto.test import context
    from auto.dblite import Database

    with context():
        db = Database('./db.sqlite3')
        init_db(db)
        store_attrs(db, 'sys')

        assert lookup(db, 'exi') == [('sys', 'exit')]
