# Tests for config module
import os
import shutil
import tempfile
import unittest
from waeup.identifier.config import (
    get_conffile_locations, find_fpscan_binary,
    )


class ConfigTests(unittest.TestCase):

    _orig_vars = {}

    def setUp(self):
        # setup virtual $HOME, $PATH and tempdirs.
        self.path_dir = tempfile.mkdtemp()
        self.home_dir = tempfile.mkdtemp()
        for var_name in ['PATH', 'HOME']:
            self._orig_vars[var_name] = os.environ.get(var_name)
        os.environ['PATH'] = self.path_dir
        os.environ['HOME'] = self.home_dir

    def tearDown(self):
        # restore $HOME, $PATH and remove tempdirs
        for var_name in ['PATH', 'HOME']:
            if self._orig_vars[var_name] is None:
                del os.environ[var_name]
            else:
                os.environ[var_name] = self._orig_vars[var_name]
        if os.path.exists(self.path_dir):
            shutil.rmtree(self.path_dir)
        if os.path.exists(self.home_dir):
            shutil.rmtree(self.home_dir)

    def test_get_conffile_locations(self):
        # we can get a list of accepted config file locations
        result = get_conffile_locations()
        assert result[0] == '/etc/waeupident.ini'
        assert result[1].endswith('.waeupident.ini')
        assert result[2].startswith(os.getcwd())

    def test_find_fpscan_binary_no_binary(self):
        # we get None if there is no binary.
        assert find_fpscan_binary() is None

    def test_find_fpscan_binary(self):
        # we get a path if a fpscan binary is in $PATH
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')
        assert find_fpscan_binary() == fake_fpscan
