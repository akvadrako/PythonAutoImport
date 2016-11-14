
from sublime import Region, status_message
from sublime_plugin import TextCommand, EventListener

active = False

# get packages from current directory
import_path = os.path.dirname(__file__)
if import_path not in sys.path:
    sys.path.insert(0, import_path)

class PythonAutoImportCommand(TextCommand):
    """Replace an auto-completed import."""

    def run(self, edit):
        global active
        if active:
            return

        active = True

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

        active = False


class PythonAutoImportListener(EventListener):
    """Listen for events."""

    def on_query_completions(self, view, prefix, locations):
        """Generate a list of importable symbols."""
        return [
            ["for\tfrom for.blah", "${1:auto.for.blah.xyz}"],
        ]

    def on_modified(self, view):
        """Check for a selection from an auto-completed import."""
        if len(view.sel()) < 1 or not view.substr(view.sel()[0]).startswith('auto.'):
            return

        view.run_command('python_auto_import')
