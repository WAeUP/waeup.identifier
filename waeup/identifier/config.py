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
from configparser import ConfigParser


#: A list of valid configuration keys.
CONF_KEYS = ['fpscan_path', 'waeup_url', 'waeup_user',
             'waeup_passwd']


CONF_SETTINGS = [
    {
        "type": "string",
        "title": "WAeUP Username",
        "desc": "Username to connect to WAeUP server",
        "section": "Server",
        "key": "waeup_user",
        "default": "grok",
    },
    {
        "type": "string",
        "title": "WAeUP Password",
        "desc": "Password to connect to WAeUP server",
        "section": "Server",
        "key": "waeup_passwd",
        "default": "grok",
    },
    {
        "type": "string",
        "title": "Server URL",
        "desc": "URL of WAeUP server to connect to",
        "section": "Server",
        "key": "waeup_url",
        "default": "",
    },
]


def get_json_settings():
    """Get settings as JSON string.
    """
    new_list = [dict(x) for x in CONF_SETTINGS]  # create a copy
    for setting in new_list:
        setting.pop('default', None)
    return json.dumps(new_list)


def get_default_settings():
    """Get tuples (<SECTION>, {<KEY>: <DEFAULTVALUE>} for config.
    """
    return [
        (setting['section'], {setting['key']: setting['default']})
        for setting in CONF_SETTINGS
        if 'default' in setting]


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


def get_config(paths=None):
    """Get a configuration.

    The paths, where config files are searched, can be given in
    `paths`, a list of paths. If no such argument is passed in, we use
    results from :func:`get_conffile_locations`.

    Returns a `configparser.ConfigParser` instance.
    """
    conf = ConfigParser()
    fpscan_path = find_fpscan_binary()
    conf['DEFAULT'] = {
        'waeup_user': 'grok',
        'waeup_passwd': 'grok',
        'waeup_url': 'localhost:8080',
        'save_passwd': '0',
        }
    if fpscan_path is not None:
        conf['DEFAULT'].update(fpscan_path=fpscan_path)
    if paths is not None:
        conffile_locations = paths
    else:
        conffile_locations = get_conffile_locations()
    conf.read(conffile_locations)
    return conf
