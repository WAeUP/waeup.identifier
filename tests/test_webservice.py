import shutil
import tempfile
import threading
import unittest
import xmlrpc.client
from waeup.identifier.config import get_config
from waeup.identifier.testing import (
    AuthenticatingXMLRPCServer, create_fake_fpm_file,
    )
from waeup.identifier.webservice import (
    store_fingerprint, get_url, get_url_from_config,
)


class HelperTests(unittest.TestCase):

    def test_get_url(self):
        # we can get completed urls from netlocations plus credentials
        assert get_url(
            'http://localhost:8080', 'bob', 'secret'
            ) == "http://bob:secret@localhost:8080"

    def test_get_url_no_scheme(self):
        # we get HTTPS if no scheme was specified
        assert get_url(
            'localhost:8080', 'bob', 'secret'
            ) == "https://bob:secret@localhost:8080"

    def test_get_url_no_port(self):
        # we can construct valid URLs w/o port.
        assert get_url(
            'https://localhost', 'bob', 'secret'
            ) == "https://bob:secret@localhost"

    def test_get_url_paths(self):
        # paths are kept in URLs
        assert get_url(
            'https://localhost:8080/app', 'bob', 'secret'
            ) == "https://bob:secret@localhost:8080/app"

    def test_get_url_from_config(self):
        # we can get valid XMLRPCable URLs from default config
        config = get_config(paths=[])  # get default config
        assert get_url_from_config(config) == (
            "https://grok:grok@localhost:8080")

    def test_get_url_from_config_w_scheme(self):
        # a scheme set in waeup_url will be respected
        config = get_config(paths=[])
        config["DEFAULT"]["waeup_url"] = "http://sample.org"
        assert get_url_from_config(config) == (
            "http://grok:grok@sample.org")

    def test_get_url_from_config_changed_creds(self):
        # changed credentials are respected
        config = get_config(paths=[])
        config["DEFAULT"]["waeup_user"] = "foo"
        config["DEFAULT"]["waeup_passwd"] = "bar"
        assert get_url_from_config(config) == "https://foo:bar@localhost:8080"

    def test_get_url_from_config_with_paths(self):
        # app paths are taken into account
        config = get_config(paths=[])
        config["DEFAULT"]["waeup_url"] = "http://sample.org/app"
        assert get_url_from_config(config) == (
            "http://grok:grok@sample.org/app")


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
        self.workdir = tempfile.mkdtemp()
        self.proxy = xmlrpc.client.ServerProxy(
            "http://mgr:mgrpw@localhost:61615")
        self.proxy.reset_student_db()

    def tearDown(self):
        shutil.rmtree(self.workdir)

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
            'get_student_fingerprints', 'ping',
            'put_student_fingerprints',
            'reset_student_db', 'system.listMethods',
            'system.methodHelp', 'system.methodSignature']

    def test_internal_put_student_fingerprints(self):
        # make sure the faked method is faked properly
        self.proxy.create_student('AB123456')
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

    def test_internal_get_student_fingerprints(self):
        self.proxy.create_student(
            'AB123456', "foo@sample.org", "foo", "bar",
            "passport.png", xmlrpc.client.Binary(b"FakedPNGFile"),
            {
                "1": xmlrpc.client.Binary(b"FP1Fake"),
                },
            )
        result1 = self.proxy.get_student_fingerprints("InvalidID")
        assert result1 == dict()
        result2 = self.proxy.get_student_fingerprints("AB123456")
        assert isinstance(result2, dict)
        assert result2["email"] == "foo@sample.org"
        assert result2["firstname"] == "foo"
        assert result2["lastname"] == "bar"
        assert result2["img_name"] == "passport.png"
        assert result2["img"].data == b"FakedPNGFile"
        assert result2["fingerprints"]["1"].data == b"FP1Fake"

    def test_store_fingerprint(self):
        # we can store a fingerprint
        self.proxy.create_student('AB123456')
        fpm_file_path = create_fake_fpm_file(self.workdir)
        result = store_fingerprint(
            "http://mgr:mgrpw@localhost:61615", "AB123456", 1, fpm_file_path)
        assert result == True
