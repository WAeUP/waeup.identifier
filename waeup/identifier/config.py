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
import os
try:
    from configparser import ConfigParser  # Python 3.x
except ImportError:
    from ConfigParser import ConfigParser  # Python 2.x


#: A list of valid configuration keys.
CONF_KEYS = ['fpscan_path', 'waeup_url', 'waeup_user',
             'waeup_passwd']


def get_conffile_locations():
    """Get a list of paths where we lookup config files.

    Most general files come first (system-wide), most specific last
    (local).
    """
    system_loc = os.path.abspath(
        os.path.join("/etc", "waeupident.ini")
        )
    home_loc = os.path.expanduser("~/.waeupident.ini")
    local_loc = os.path.abspath("waeupident.ini")
    return [system_loc, home_loc, local_loc]


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


JSON_SETTINGS = [
    {
        "type": "string",
        "title": "WAeUP Username",
        "desc": "Username to connect to WAeUP server",
        "section": "Server",
        "key": "waeup_user"
    },
]


DEFAULT_SETTINGS = [
    ('Server', {'waeup_user': 'grok'}),
]
