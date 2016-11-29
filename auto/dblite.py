
from auto.pool import Pool, PoolItem
from auto.func import trace

import sqlite3

class Column:
    def __init__(self, name, type='TEXT', constraint=''):
        self.name = name
        self.type = type
        self.constraint = constraint

    @property
    def sql(self):
        return '%s %s %s' % (self.name, self.type, self.constraint) 

class Schema:
    def __init__(self, name, *columns):
        self.name = name
        self.columns = columns

    @property
    def create_sql(self):
        return ''.join([
            'CREATE TABLE IF NOT EXISTS ',
            self.name,
            '(',
            ', '.join(c.sql for c in self.columns),
            ')',
        ])

class Database:
    def __init__(self, path):
        self.pool = Pool(lambda: Connection(path))
        
    def __call__(self, *args):
        with self.pool() as conn:
            conn(*args)

    def add_table(self, schema):
        self(schema.create_sql)

    def insert(self, table_name, **attrs):
        keys, values = zip(*attrs.items())

        with self.pool() as conn:
            conn('INSERT INTO ' + table_name + 
                '(' + ', '.join(keys) +  ')' +
                ' VALUES ' + '(' + ', '.join(['?'] * len(keys)) +  ')',
                values)

    def replace(self, table_name, **attrs):
        keys, values = zip(*attrs.items())

        with self.pool() as conn:
            conn('REPLACE INTO ' + table_name + 
                '(' + ', '.join(keys) +  ')' +
                ' VALUES ' + '(' + ', '.join(['?'] * len(keys)) +  ')',
                values)

    def delete(self, table_name, **attrs):
        keys, values = zip(*attrs.items())

        with self.pool() as conn:
            conn('DELETE FROM ' + table_name + ' WHERE ' +
                ' AND '.join('%s = ?' % k for k in keys),
                values)

    def get(self, table_name, **attrs):
        keys, values = zip(*attrs.items())

        with self.pool() as conn:
            cursor = conn('SELECT * from ' + table_name + ' WHERE ' +
                ' AND '.join('%s = ?' % k for k in keys),
                values)

            if cursor.rowcount > 1:
                raise RuntimeError('too many results')

            return cursor.fetchone()


class Connection(PoolItem):
    """Wrap an SQLite3 connection."""

    @trace
    def __init__(self, path):

        self._raw = sqlite3.connect(path,
            isolation_level="DEFERRED",
            detect_types=sqlite3.PARSE_DECLTYPES)
        self._raw.row_factory = sqlite3.Row 

    def __call__(self, *args):
        return self._raw.execute(*args)

    # PoolItem

    def reset(self):
        self._raw.commit()

    def close(self):
        self._raw.rollback()
        self._raw.close()