
import sys, os.path
sys.path.insert(0, os.path.dirname(__file__) + '/stub')

import plugin
from sublime import Region, View, Edit

from auto.test import patch
from auto.mock import Mock, Call

def test_completions():

    def lookup(db, prefix):
        assert prefix == 'exi'
        return [('sys', 'exit')]
    
    listener = plugin.PythonAutoImportListener()

    with patch(plugin, 'lookup', lookup):
        completions = listener.on_query_completions(None, 'exi', None)
    
    assert completions == [
        ('exit\tfrom sys', '${1:auto.sys.exit}'),
    ]

def test_on_modified():

    view = View()
    view.insert(Edit(), 0, 'auto.sys.exit')
    view.selection.add(Region(0,13))
    view.run_command = Mock()

    listener = plugin.PythonAutoImportListener()
    listener.on_modified(view)

    assert view.run_command._calls == [
        Call('python_auto_import')
    ]

def test_import_command():
    view = View()
    view.insert(Edit(), 0, 'auto.sys.exit')
    view.selection.add(Region(0, 13))

    cmd = plugin.PythonAutoImportCommand(view)
    cmd.run(Edit())

    assert view.substr(Region(0, len(view))) == \
        'from sys import exit\nexit'