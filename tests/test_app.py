import os
import shutil
import tempfile
import unittest
from tkinter import Menu
from waeup.identifier.app import FPScanApplication

#
# Some infos about testing tk GUI stuff:
#
# buttons can be 'clicked' via 'invoke()'
#

class AppTests(unittest.TestCase):

    _orig_vars = {}

    def setup_virtual_home(self):
        # setup virtual $HOME, $PATH and tempdirs.
        self.path_dir = tempfile.mkdtemp()
        self.home_dir = tempfile.mkdtemp()
        for var_name in ['PATH', 'HOME']:
            self._orig_vars[var_name] = os.environ.get(var_name)
        os.environ['PATH'] = self.path_dir
        os.environ['HOME'] = self.home_dir
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')

    def teardown_virtual_home(self):
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

    def setUp(self):
        self.setup_virtual_home()
        self.app = FPScanApplication()
        #self.app.wait_visibility()

    def tearDown(self):
        self.app.destroy()
        self.teardown_virtual_home()

    def test_create(self):
        # we can create app instances
        assert self.app is not None

    def test_title(self):
        # The app will have a certain title
        self.assertEqual(self.app.master.title(), 'WAeUP Identifier')

    def test_menubar_exists(self):
        # we have (exactly) 1 menubar
        menus = [x for x in self.app.children.values()
                 if isinstance(x, Menu)]
        assert len(menus) == 1

    def test_menubar_hasquit(self):
        # the menubar has a quit-item
        menubar = self.app.menubar
        filemenu = self.app.menu_file
        filemenu.invoke('Quit')  # must not raise any error

    def DISABLED_test_menubar_hasabout(self):
        # the menubar has an help-item
        # XXX: Currently disabled as 'about' generates a modal dialog we
        #      cannot stop from here.
        menubar = self.app.menubar
        helpmenu = self.app.menu_help
        helpmenu.invoke('About WAeUP Identifier')  # must not raise any error

    def test_footer_bar(self):
        # we can set text of the footer bar
        self.app.footer_bar['text'] = 'My Message.'
        self.assertEqual(
            self.app.footer_bar['text'], 'My Message.')
