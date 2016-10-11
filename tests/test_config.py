# Tests for config module
import json
import os
import pytest
from waeup.identifier.config import (
    get_conffile_location, find_fpscan_binary, get_config, CONF_KEYS,
    get_json_settings, get_default_settings
    )
from waeup.identifier.testing import VirtualHomingTestCase


@pytest.fixture(scope="function")
def home_dir(request, monkeypatch, tmpdir):
    """A py.test fixture providing a temporary user home.

    It also sets PATH to contain this temporary home as only entry.
    """
    tmpdir.mkdir("home")
    monkeypatch.setenv("HOME", str(tmpdir / "home"))
    monkeypatch.setenv("PATH", str(tmpdir / "home"))
    return tmpdir / "home"


def test_get_json_settings_empty():
    # empty settings are possible
    assert get_json_settings([]) == '[]'


def test_get_json_settings_no_default():
    # we discard `default` keys from settings
    result = get_json_settings(
        [{'section': 'foo', 'key': 'bar', 'default': 'baz'}, ])
    assert json.loads(result) == [{"key": "bar", "section": "foo"}]


class Test_get_default_settings(object):
    # tests for `config.get_default_settings()`.

    def test_get_default_settings(self, home_dir):
        # we can get default of a single setting
        result = get_default_settings(
            [{'section': 'foo', 'key': 'bar', 'default': 'baz'}, ])
        assert result == [("foo", dict(bar="baz"))]

    def test_get_default_settings_ignore_no_default(self, home_dir):
        # we ignore settings w/o a default value
        result = get_default_settings([{'section': 'foo', 'key': 'bar'}])
        assert result == []

    def test_get_default_settings_multi_in_section(self, home_dir):
        # we put several settings per section in one entry
        result = get_default_settings(
            [
                {'section': 'foo', 'key': 'key1', 'default': 'bar1'},
                {'section': 'foo', 'key': 'key2', 'default': 'bar2'}])
        assert result == [
            ("foo", dict(key1="bar1")), ("foo", dict(key2="bar2"))]

    def test_get_default_settings_fpscan_not_found(self, home_dir):
        # we treat `fpscan_path` special.
        result = get_default_settings(
            [{'section': 'foo', 'key': 'fpscan_path', 'default': 'bar'}])
        assert result == [("foo", dict(fpscan_path="bar"))]

    def test_get_default_settings_fpscan_found(self, home_dir):
        # we treat `fpscan_path` special and get a valid path.
        home_dir.join("fpscan").write("just a fake script")
        result = get_default_settings(
            [{'section': 'foo', 'key': 'fpscan_path', 'default': 'bar'}])
        path = str(home_dir / "fpscan")
        assert result == [("foo", dict(fpscan_path=path))]


def test_get_conffile_location(home_dir):
    # we can get a config file location path
    result = get_conffile_location()
    assert result == str(home_dir / '.waeupident.ini')


class Test_find_fpscan_binary(object):

    def test_find_fpscan_binary_no_binary(self, home_dir):
        # we get None if there is no binary.
        assert find_fpscan_binary() is None

    def test_find_fpscan_binary(self, home_dir):
        # we get a path if a fpscan binary is in $PATH
        fake_fpscan_path = home_dir / 'fpscan'
        fake_fpscan_path.write('Just a fake script.')
        assert find_fpscan_binary() == str(fake_fpscan_path)

    def test_find_fpscan_binary_valid_custom(self, home_dir):
        # we accept proposed paths if given and valid
        fake_fpscan_path = home_dir / 'fpscan'
        fake_fpscan_path.write('Just a fake')
        assert find_fpscan_binary(
            str(fake_fpscan_path)) == str(fake_fpscan_path)

    def test_find_fpscan_binary_valid_custom(self, home_dir):
        # we accept proposed paths if given and valid
        fake_fpscan_path = home_dir / 'fpscan'
        fake_fpscan_path.write('Just a fake')
        assert find_fpscan_binary(str(fake_fpscan_path)) == str(fake_fpscan_path)



class ConfigTests(VirtualHomingTestCase):

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
