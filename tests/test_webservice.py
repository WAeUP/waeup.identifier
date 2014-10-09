import threading
import unittest
import xmlrpc.client
from waeup.identifier.testing import AuthenticatingXMLRPCServer


class WebserviceTests(unittest.TestCase):

    server = None
    server_thread = None

    @classmethod
    def setUpClass(cls):
        # start fake server in background once for all webservice tests
        cls.server = AuthenticatingXMLRPCServer('127.0.0.1', 61616)
        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.proxy = xmlrpc.client.ServerProxy(
            "http://mgr:mgrpw@localhost:61616")

    def test_internal_ping(self):
        # make sure the fake xmlrpc server works
        assert self.proxy.ping(42) == ['pong', 42]

    def test_internal_auth(self):
        # make sure our fake xmlrpc server requires authentication
        proxy = xmlrpc.client.ServerProxy("http://localhost:61616")
        self.assertRaises(
            xmlrpc.client.ProtocolError, proxy.ping, 42)
