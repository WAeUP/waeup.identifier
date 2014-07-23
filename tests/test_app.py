import os
import shutil
import tempfile
import unittest
from tkinter import Menu
from waeup.identifier.app import FPScanApplication, detect_scanners
from waeup.identifier.testing import VirtualHomeProvider

#
# Some infos about testing tk GUI stuff:
#
# buttons can be 'clicked' via 'invoke()'
#

class HelperTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()

    def tearDown(self):
        self.teardown_virtual_home()

    def test_detect_scanners_no_fpscan(self):
        # w/o fpscan we will not find any scanner
        assert detect_scanners('invalid_path') == []

    def test_detect_scanners_non_executable(self):
        # the given file must exists and be executable
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('not an executable')
        assert detect_scanners(fake_fpscan) == []

    def test_detect_scanners_illegal_filenames(self):
        # dangerous paths are rejected
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('exit 0')
        assert detect_scanners(fake_fpscan + '; rm -rf /') == []


class AppTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')
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
