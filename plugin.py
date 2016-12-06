"""Sublime Text 3 Python Auto Import Plugin."""

import sys, os.path
sys.path.insert(0, os.path.dirname(__file__))

from sublime import Region, status_message
from sublime_plugin import TextCommand, EventListener

from auto.scanmod import update, lookup
from auto.dblite import Database
from auto.core import Globals
from auto.timer import Timer

from threading import Lock

g = Globals(
    db=Database(os.path.dirname(__file__) + './db.sqlite3'),
    timer=None,
    lock=Lock(),
)

class PythonAutoImportCommand(TextCommand):
    """Replace an auto-completed import."""

    def run(self, edit):
        if not g.lock.acquire(False):
            return

        region = self.view.sel()[0]
        parts = self.view.substr(region).split('.')
        status_message('auto importing %s' % '.'.join(parts))

        # sanity check
        if parts[0] != 'auto':
            return

        # update selection
        self.view.sel().subtract(region)
        if(len(self.view.sel()) == 0):
            after = Region(region.end(), region.end())
            self.view.sel().add(after)

        # replace selection with naked attribute name
        self.view.replace(edit, region, parts[-1])

        # add the imports to the top of the file
        imports = self.view.find('^(import|from)', 0) or Region(0, 0)
        mod = '.'.join(parts[1:-1])
        self.view.insert(edit, imports.begin(),
            'from %s import %s\n' % (mod, parts[-1]))

        g.lock.release()


class PythonAutoImportListener(EventListener):
    """Listen for events."""

    def on_query_completions(self, view, prefix, locations):
        """Generate a list of importable symbols."""
        results = []
        for c in lookup(g.db, prefix):
            results.append((
                '%s\tfrom %s' % (c[1], c[0]),
                '${1:auto.%s.%s}' % (c[0], c[1]),
            ))

        return results

    def on_modified(self, view):
        """Check for a selection from an auto-completed import."""
        if len(view.sel()) < 1 or not view.substr(view.sel()[0]).startswith('auto.'):
            return

        view.run_command('python_auto_import')

def plugin_loaded():
    g.timer = Timer(lambda: update(g.db), 5)

def plugin_unloaded():
    g.timer.stop()
    