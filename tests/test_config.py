# Tests for config module
import os
import unittest
from waeup.identifier.config import (
    get_conffile_locations, find_fpscan_binary,
    )


class ConfigTests(unittest.TestCase):

    _orig_vars = {}

    def setUp(self):
        # setup virtual $HOME, $PATH and tempdirs.
        for var_name in ['PATH', 'HOME']:
            self._orig_vars[var_name] = os.environ.get(var_name)
            if self._orig_vars[var_name] is None:
                continue
            del os.environ[var_name]

    def tearDown(self):
        # restore $HOME, $PATH and remove tempdirs
        for var_name in ['PATH', 'HOME']:
            if self._orig_vars[var_name] is None:
                continue
            os.environ[var_name] = self._orig_vars[var_name]

    def test_get_conffile_locations(self):
        # we can get a list of accepted config file locations
        result = get_conffile_locations()
        assert result[0] == '/etc/waeupident.ini'
        assert result[1].endswith('.waeupident.ini')
        assert result[2].startswith(os.getcwd())

    def test_find_fpscan_binary_no_binary(self):
        # we get None if there is no binary.
        assert find_fpscan_binary() is None
