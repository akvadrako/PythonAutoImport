"""Little libs."""

import logging

log = logging.getLogger(__name__)

################################################

def mtime(path):
    """Return mtime for path, default to epoch."""
    import os
    from datetime import datetime

    s = os.stat(path)
    return datetime.utcfromtimestamp(s.st_mtime if s else 0)

def test_mtime():
    pass

################################################

def scan_modules():
    """Yields the name of each module found.

    This is based off the Python 2.7 pydoc.py module.
    """
    import sys, pkgutil
    
    def _onerror(pkg):
        log.error('error importing %s', pkg)

    for modname in sys.builtin_module_names:
        yield modname

    for importer, modname, ispkg in pkgutil.walk_packages(onerror=_onerror):
        yield modname

def test_scan_modules():
    pass

##############################################