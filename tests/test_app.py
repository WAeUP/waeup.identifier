import unittest
from tkinter import Menu
from waeup.identifier.app import FPScanApplication

#
# Some infos about testing tk GUI stuff:
#
# buttons can be 'clicked' via 'invoke()'
#

class AppTests(unittest.TestCase):

    def setUp(self):
        self.app = FPScanApplication()
        #self.app.wait_visibility()

    def tearDown(self):
        self.app.destroy()

    def test_create(self):
        # we can create app instances
        assert self.app is not None

    def test_size(self):
        # The app will have four cols and five rows
        self.assertEqual(self.app.size(), (4,5))

    def test_menubar_exists(self):
        # we have (exactly) 1 menubar
        menus = [x for x in self.app.children.values()
                 if isinstance(x, Menu)]
        assert len(menus) == 1

    def test_menubar_hasquit(self):
        # the menubar has a quit-item
        menubar = self.app.menubar
        filemenu = [x for x in menubar.children.values()][0]
        assert self.app.winfo_exists()
        filemenu.invoke('Quit')  # must not raise any error

    def test_menubar_cmd1(self):
        # we can click the My Cmd in menubar
        menubar = self.app.menubar
        filemenu = [x for x in menubar.children.values()][0]
        filemenu.invoke('My Cmd 1')  # must not raise any error
