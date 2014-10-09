import threading
import unittest
import xmlrpc.client
from waeup.identifier.testing import (
    AuthenticatingXMLRPCServer, fake_student_db,
    )
from waeup.identifier.testing import fake_student_db


class WebserviceTests(unittest.TestCase):

    server = None
    server_thread = None

    @classmethod
    def setUpClass(cls):
        # start fake server in background once for all webservice tests
        cls.server = AuthenticatingXMLRPCServer('127.0.0.1', 61615)
        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.proxy = xmlrpc.client.ServerProxy(
            "http://mgr:mgrpw@localhost:61615")

    def test_internal_ping(self):
        # make sure the fake xmlrpc server works
        assert self.proxy.ping(42) == ['pong', 42]

    def test_internal_auth(self):
        # make sure our fake xmlrpc server requires authentication
        proxy = xmlrpc.client.ServerProxy(
            "http://localhost:61615")
        self.assertRaises(
            xmlrpc.client.ProtocolError, proxy.ping, 42)

    def test_internal_methods(self):
        # the following methods are available
        assert sorted(self.proxy.system.listMethods()) == [
            'create_student',
            'ping', 'put_student_fingerprints',
            'reset_student_db', 'system.listMethods',
            'system.methodHelp', 'system.methodSignature']

    def test_internal_put_student_fingerprints(self):
        # make sure the faked method is faked properly
        self.proxy.create_student('AB123456')
        assert fake_student_db == {'AB123456': {}}
        # invalid student id
        self.assertRaises(
            xmlrpc.client.Fault,
            self.proxy.put_student_fingerprints, 'invalid-id')
        # fingerprint dict not a dict
        self.assertRaises(
            xmlrpc.client.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', 'not-a-dict')
        # invalid fingerprint file type
        self.assertRaises(
            xmlrpc.client.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', {'1': 12})
        # invalid file format
        self.assertRaises(
            xmlrpc.client.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', {
                '1': xmlrpc.client.Binary(b'not-an-fpm-file')}
            )
        # valid fingerprint dict
        assert self.proxy.put_student_fingerprints(
            'AB123456', {
                '1': xmlrpc.client.Binary(b'FP1-faked-fpm-file')}
            ) == True
        # empty fingerprint dict
        assert self.proxy.put_student_fingerprints(
            'AB123456', {}) == False
