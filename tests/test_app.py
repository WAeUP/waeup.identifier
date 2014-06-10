import unittest
from waeup.identifier.app import FPScanApplication

class AppTests(unittest.TestCase):

    def test_create(self):
        # we can create app instances
        app = FPScanApplication()

    def test_size(self):
        # The app will have four cols and five rows
        app = FPScanApplication()
        self.assertEqual(app.size(), (4,5))
