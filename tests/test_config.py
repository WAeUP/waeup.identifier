# Tests for config module
import os
import shutil
import tempfile
import unittest
from waeup.identifier.config import (
    get_conffile_locations, find_fpscan_binary, get_config,
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

    def test_find_fpscan_binary_valid_custom(self):
        # we accept proposed paths if given and valid
        fake_fpscan_path = os.path.join(self.home_dir, 'fpscan')
        open(fake_fpscan_path, 'w').write('Just a fake')
        assert find_fpscan_binary(fake_fpscan_path) == fake_fpscan_path

    def test_find_fpscan_binary_invalid(self):
        # we get None if given paths are invalid
        assert find_fpscan_binary('iNvAlIdPaTh') is None

    def test_find_fpscan_binary_fallback(self):
        # we find fpscans paths in $PATH if custom ones are invalid
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')
        assert find_fpscan_binary('invalid_path') == fake_fpscan

    def test_get_config(self):
        # we can get valid configs
        conf = get_config()
        assert conf.get('DEFAULT', 'waeup_user') == 'grok'
        assert conf.get('DEFAULT', 'waeup_passwd') == 'grok'
