# Tests for config module
import json
import os
import waeup.identifier.config
from waeup.identifier.config import (
    get_conffile_locations, find_fpscan_binary, get_config, CONF_KEYS,
    get_json_settings,
    )
from waeup.identifier.testing import VirtualHomingTestCase


def test_get_json_settings_empty(monkeypatch):
    waeup.identifier.config.CONF_SETTINGS = []
    assert get_json_settings() == '[]'


def test_get_json_settings_no_default(monkeypatch):
    # we discard `default` keys from settings
    waeup.identifier.config.CONF_SETTINGS = [
        {'section': 'foo', 'key': 'bar', 'default': 'baz'}, ]
    result = get_json_settings()
    assert json.loads(result) == [{"key": "bar", "section": "foo"}]


class ConfigTests(VirtualHomingTestCase):

    def test_get_conffile_locations(self):
        # we can get a list of accepted config file locations
        result = get_conffile_locations()
        assert result[0] == '/etc/waeupident.ini'
        assert result[1] == os.path.join(self.home_dir, '.waeupident.ini')
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
        assert conf.get('DEFAULT', 'waeup_url') == 'localhost:8080'

    def test_get_config_fpscan_path(self):
        # we get a valid fpscan path if avail.
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')
        conf = get_config()
        assert conf.get('DEFAULT', 'fpscan_path') == fake_fpscan

    def test_get_config_from_single_file(self):
        # configs can be read from a file
        conf_path = os.path.join(self.home_dir, 'config.conf')
        open(conf_path, 'w').write('[DEFAULT]\nwaeup_user=user1\n')
        conf = get_config(paths=[conf_path])
        assert conf.get('DEFAULT', 'waeup_user') == 'user1'
        assert conf.get('DEFAULT', 'waeup_passwd') == 'grok'

    def test_get_config_two_files(self):
        # configs can be read from two or more files
        conf1 = os.path.join(self.home_dir, 'conf1.cfg')
        conf2 = os.path.join(self.home_dir, 'conf2.cfg')
        open(conf1, 'w').write('[DEFAULT]\nwaeup_user=user1\n')
        open(conf2, 'w').write('[DEFAULT]\nwaeup_user=user2\n')
        conf = get_config(paths=[conf1, conf2])
        assert conf.get('DEFAULT', 'waeup_user') == 'user2'
        conf = get_config(paths=[conf2, conf1])
        assert conf.get('DEFAULT', 'waeup_user') == 'user1'

    def test_all_conf_keys_appear(self):
        # make sure that normally CONF_KEYS appear in default config
        conf = get_config()
        conf_dict = dict(conf.defaults())
        for key in CONF_KEYS:
            # some keys are not neccessarily available...
            if key in ['fpscan_path', ]:
                continue
            assert key in conf_dict
