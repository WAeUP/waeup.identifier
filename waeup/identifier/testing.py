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
import shutil
import tempfile
import unittest


class VirtualHomeProvider(object):
    """A unittest mixin for tests where a virtual home is needed.
    """
    _orig_vars = {}

    def setup_virtual_home(self):
        """Setup virtual $HOME, $PATH and tempdirs.
        """
        self.path_dir = tempfile.mkdtemp()
        self.home_dir = tempfile.mkdtemp()
        for var_name in ['PATH', 'HOME']:
            self._orig_vars[var_name] = os.environ.get(var_name)
        os.environ['PATH'] = self.path_dir
        os.environ['HOME'] = self.home_dir

    def teardown_virtual_home(self):
        """Restore $HOME, $PATH and remove tempdirs.
        """
        for var_name in ['PATH', 'HOME']:
            if self._orig_vars[var_name] is None:
                del os.environ[var_name]
            else:
                os.environ[var_name] = self._orig_vars[var_name]
        if os.path.exists(self.path_dir):
            shutil.rmtree(self.path_dir)
        if os.path.exists(self.home_dir):
            shutil.rmtree(self.home_dir)


class VirtualHomingTestCase(unittest.TestCase, VirtualHomeProvider):
    """A unittest test case that sets up virtual homes.

    Provides `self.path_dir` and `self.home_dir` pointing to temporary
    directories set in ``$PATH`` and ``$HOME`` respectively.
    """
    def setUp(self):
        self.setup_virtual_home()

    def tearDown(self):
        self.teardown_virtual_home()
