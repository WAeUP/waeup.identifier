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
from configparser import ConfigParser


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


def find_fpscan_binary():
    """Find the path to an fpscan binary.

    We search the paths in $PATH and look for a script called
    ``fpscan``.
    """
    paths = os.environ.get('PATH', '').split(':')
    for path in paths:
        bin_path = os.path.join(path, 'fpscan')
        if os.path.exists(bin_path):
            return bin_path
    return None


def get_config():
    """Get a configuration.
    """
    conf = ConfigParser()
    conf['DEFAULT'] = {
        'waeup_user': 'grok',
        'waeup_passwd': 'grok',
        'save_passwd': '0',
        'waeup_url': None,
        }
    return conf
