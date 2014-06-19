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
