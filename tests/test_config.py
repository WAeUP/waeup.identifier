# Tests for config module
import os
import unittest
from waeup.identifier.config import get_conffile_locations


class ConfigTests(unittest.TestCase):

    def test_get_conffile_locations(self):
        # we can get a list of accepted config file locations
        result = get_conffile_locations()
        assert result[0] == '/etc/waeupident.ini'
        assert result[1].endswith('.waeupident.ini')
        assert result[2].startswith(os.getcwd())
