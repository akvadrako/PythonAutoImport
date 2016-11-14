
from auto.pool import Pool, PoolItem

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
            conn.execute(*args)

    def add_table(self, schema):
        self(schema.create_sql)

    def get(self, table_name, **keys):
        keys, values = zip(keys.items())

        cursor = self('SELECT * from table_name WHERE ' +
            ' AND '.join('%s = ?' % k for k in keys),
            values)

        if cursor.rowcount > 1:
            raise RuntimeError('too many results')

        return cursor.fetchone()


class Connection(PoolItem):
    def __init__(self, path):
        self.conn = sqlite3.connect(self.path,
            isolation_level=sqlite3.DEFERRED,
            detect_types=sqlite3.PARSE_DECLTYPES)

    # PoolItem

    def reset(self):
        self.conn.commit()

    def close(self):
        self.conn.rollback()
        self.conn.close()