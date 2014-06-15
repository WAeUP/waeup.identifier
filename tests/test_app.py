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
        self.assertEqual(self.app.size(), (4,6))

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

    def test_btn_calc(self):
        # we can invoke the calc button
        self.app.feet.set('12.12')
        self.assertEqual(self.app.meters.get(), '')
        self.app.btn_calc.invoke()
        self.assertEqual(self.app.meters.get(), '3.694226')

    def test_btn_calc_invalid_value(self):
        # invalid values are ignored
        self.app.feet.set('not-a-numeric-value')
        self.app.btn_calc.invoke()

    def test_footer_bar(self):
        # we can set text of the footer bar
        self.app.footer_bar['text'] = 'My Message.'
        self.assertEqual(
            self.app.footer_bar['text'], 'My Message.')
