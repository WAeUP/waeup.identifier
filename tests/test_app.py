import os
import shutil
import stat
import tempfile
import unittest
from tkinter import Menu
from waeup.identifier.app import (
    FPScanApplication, detect_scanners, check_path
    )
from waeup.identifier.testing import (
    VirtualHomeProvider, VirtualHomingTestCase,
    )

#
# Some infos about testing tk GUI stuff:
#
# buttons can be 'clicked' via 'invoke()'
#


class HelperTests(VirtualHomingTestCase):

    def test_check_path_not_existing(self):
        # the path given must exist
        self.assertRaises(ValueError, check_path, 'not-existing-path')

    def test_check_path_not_executable(self):
        # the path given must be an executable
        path = os.path.join(self.path_dir, 'some_exe')
        open(path, 'w').write('not an executable')
        self.assertRaises(ValueError, check_path, path)

    def test_check_path_with_shell_commands(self):
        # evil shell commands in path are quoted
        path = os.path.join(self.path_dir, 'exe; echo "Hi"')
        open(path, 'w').write('my executable')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        self.assertRaises(ValueError, check_path, path)

    def test_check_path(self):
        # valid paths are returned unchanged
        path = os.path.join(self.path_dir, 'my.exe')
        open(path, 'w').write('my script')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        assert check_path(path) == path

    def test_check_path_irregular_chars(self):
        # unusual chars in filenames are handled
        path = os.path.join(self.path_dir, 'my"special".exe')
        open(path, 'w').write('my script')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        self.assertRaises(ValueError, check_path, path)

    def test_check_path_empty_filename(self):
        # filenames must have at least one char.
        self.assertRaises(ValueError, check_path, '')

    def test_check_path_directory(self):
        # directories are not accepted.
        self.assertRaises(ValueError, check_path, self.path_dir)

    def test_check_path_none(self):
        # we cope with `None` values
        self.assertRaises(ValueError, check_path, None)

    def test_detect_scanners_no_fpscan(self):
        # w/o fpscan we will not find any scanner
        self.assertRaises(ValueError, detect_scanners, 'invalid_path')

    def test_detect_scanners_no_scanners(self):
        # with no scanners avail. we will get an empty list
        path = os.path.join(self.path_dir, 'fpscan')
        open(path, 'w').write('#!/usr/bin/python\nprint("0")\n')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        assert detect_scanners(path) == []


class AppTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('Just a fake script.')
        os.chmod(fake_fpscan, os.stat(fake_fpscan).st_mode | stat.S_IEXEC)
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
