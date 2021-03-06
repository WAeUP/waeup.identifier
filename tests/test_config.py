# Tests for config module
import json
from waeup.identifier.config import (
    get_conffile_location, find_fpscan_binary, get_config, CONF_KEYS,
    get_json_settings, get_default_settings
    )


class TestHelpers(object):
    # tests for functions that do not need much ado.

    def test_get_json_settings_empty(self):
        # empty settings are possible
        assert get_json_settings([]) == '[]'

    def test_get_json_settings_no_default(self):
        # we discard `default` keys from settings
        result = get_json_settings(
            [{'section': 'foo', 'key': 'bar', 'default': 'baz'}, ])
        assert json.loads(result) == [{"key": "bar", "section": "foo"}]

    def test_get_conffile_location(self, home_dir):
        # we can get a config file location path
        result = get_conffile_location()
        assert result == str(home_dir / '.waeupident.ini')


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

    def test_find_fpscan_binary_invalid(self, home_dir):
        # we get None if given paths are invalid
        assert find_fpscan_binary('iNvAlIdPaTh') is None

    def test_find_fpscan_binary_fallback(self, home_dir):
        # we find fpscans paths in $PATH if custom ones are invalid
        fake_fpscan = home_dir / "fpscan"
        fake_fpscan.write('Just a fake script')
        assert find_fpscan_binary('invalid_path') == str(fake_fpscan)


class Test_get_config(object):

    def test_get_config(self):
        # we can get valid configs
        conf = get_config()
        assert conf.get('DEFAULT', 'waeup_url') == 'localhost:8080'

    def test_get_config_fpscan_path(self, home_dir):
        # we get a valid fpscan path if avail.
        fake_fpscan = home_dir / "fpscan"
        fake_fpscan.write('Just a fake script.')
        conf = get_config()
        assert conf.get('DEFAULT', 'fpscan_path') == str(fake_fpscan)

    def test_get_config_from_single_file(self, home_dir):
        # configs can be read from a file
        conf_path = home_dir / 'config.conf'
        conf_path.write('[DEFAULT]\nfpscan_path=some_value\n')
        conf = get_config(path=str(conf_path))
        assert conf.get('DEFAULT', 'fpscan_path') == 'some_value'
        assert conf.get('DEFAULT', 'waeup_url') == 'localhost:8080'

    def test_get_config_from_single_file_overwrites(self, home_dir):
        # configs can be read from a file, its values overwrite existing ones
        conf_path = home_dir / 'config.conf'
        conf_path.write('[DEFAULT]\nwaeup_url=otherhost:8181\n')
        conf = get_config(path=str(conf_path))
        assert conf.get('DEFAULT', 'waeup_url') == 'otherhost:8181'

    def test_all_conf_keys_appear(self, home_dir):
        # make sure that normally CONF_KEYS appear in default config
        conf = get_config()
        conf_dict = dict(conf.defaults())
        for key in CONF_KEYS:
            # some keys are not neccessarily available...
            if key in ['fpscan_path', ]:
                continue
            assert key in conf_dict
