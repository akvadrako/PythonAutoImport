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
        if not rec.path:
            return
        
        # check if the record needs to be updated
        if mtime(rec.path) <= rec.modified:
            return

    log.debug('updating attributes for %s', modname)
    db('DELETE FROM attrs WHERE module=?', modname)

    mod = import_module(modname)
    for attr in dir(mod):
        db.insert('attrs',
            name=attr,
            module=modname,
        )

    db.replace('modules',
        name=modname,
        path=mod.__file__,
        modified=mtime(mod.__file__),
    )

def update(db):
    """Update db."""
    init_db(db)
    for modname in scan_modules():
        store_attrs(db, modname)

def lookup(db, prefix):
    """Return a list of completions for prefix"""
    return []

def test_scanmod():
    from auto.test import context
    from auto.dblite import Database

    with context():
        db = Database('./db.sqlite3')
        init_db(db)
        store_attrs(db, 'sys')

        assert lookup(db, 'exi') == ['sys.exit']
