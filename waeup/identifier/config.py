#
#    waeup.identifier - identifiy WAeUP Kofa students biometrically
#    Copyright (C) 2014  Uli Fouquet, WAeUP Germany
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json
import os
import pkg_resources
from kivy.config import ConfigParser


#: A list of valid configuration keys.
CONF_KEYS = ['fpscan_path', 'waeup_url']

CONF_SETTINGS = [
    {
        "type": "title",
        "title": "Version: %s" % pkg_resources.get_distribution(
            'waeup.identifier').version,
    },
    {
        "type": "title",
        "title": "Server",
    },
    {
        "type": "string",
        "title": "Server URL",
        "desc": "URL of WAeUP server to connect to",
        "section": "Server",
        "key": "waeup_url",
        "default": "https://localhost:8080",
    },
    {
        "type": "title",
        "title": "fpscan Utility",
    },
    {
        "type": "path",
        "title": "fpscan path",
        "desc": "Path to the fpscan binary",
        "section": "fpscan",
        "key": "fpscan_path",
        "default": "<unset>",
    },
]


def get_json_settings(settings=CONF_SETTINGS):
    """Get settings as JSON string.

    These are basically the `CONF_SETTINGS` with defaults removed.
    """
    new_list = [dict(x) for x in settings]  # create a copy
    for setting in new_list:
        setting.pop('default', None)
    return json.dumps(new_list)


def get_default_settings(settings=CONF_SETTINGS):
    """Get tuples (<SECTION>, {<KEY>: <DEFAULTVALUE>} for config.

    If <KEY> is "fpscan_path", the default is set to the result of
    `find_fpscan_binary()`. If no path can be detected, we set "<unset>"
    as fpscan_path default.
    """
    result = []
    for setting in settings:
        default = setting.get('default', None)
        if default is None:
            continue
        if setting['key'] == 'fpscan_path':
            default = "%s" % (find_fpscan_binary() or default)
        result.append((setting['section'], {setting['key']: default}))
    return result


def get_conffile_location():
    """Get a path where we lookup the app config files.
    """
    home_loc = os.path.expanduser("~/.waeupident.ini")
    return home_loc


def find_fpscan_binary(path=None):
    """Find the path to an fpscan binary.

    We search the paths in $PATH and look for a script called
    ``fpscan``.

    If `path` is given, we consider it first.
    """
    if path and os.path.exists(path):
        return path
    paths = os.environ.get('PATH', '').split(':')
    for path in paths:
        bin_path = os.path.join(path, 'fpscan')
        if os.path.exists(bin_path):
            return bin_path
    return None


def get_config(path=None):
    """Get a configuration.

    The path, where a config file is searched, can be given in
    `path`, a string. If no such argument is passed in, we use
    results from :func:`get_conffile_locations`.

    Returns a `kivy.config.ConfigParser` instance.
    """
    conf = ConfigParser()
    fpscan_path = find_fpscan_binary()
    conf['DEFAULT'] = {
        'waeup_url': 'localhost:8080',
        'save_passwd': '0',
        }
    if fpscan_path is not None:
        conf['DEFAULT'].update(fpscan_path=fpscan_path)
    if path is not None:
        conffile_location = path
    else:
        conffile_location = get_conffile_location()
    conf.read(conffile_location)
    return conf
