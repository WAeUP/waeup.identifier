import shutil
import socket
import tempfile
import threading
import unittest
try:
    import xmlrpc.client as xmlrpcclient   # Python 3.x
except ImportError:
    import xmlrpclib as xmlrpcclient       # Python 2.x
from waeup.identifier.config import get_config
from waeup.identifier.testing import (
    AuthenticatingXMLRPCServer, create_fake_fpm_file,
    )
from waeup.identifier.webservice import (
    store_fingerprint, get_fingerprints, get_url, get_url_from_config,
)


class TestHelpers(object):

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
        config = get_config(path=None)  # get default config
        assert get_url_from_config(config) == (
            "https://grok:grok@localhost:8080")

    def test_get_url_from_config_w_scheme(self):
        # a scheme set in waeup_url will be respected
        config = get_config(path=None)
        config["DEFAULT"]["waeup_url"] = "http://sample.org"
        assert get_url_from_config(config) == (
            "http://grok:grok@sample.org")

    def test_get_url_from_config_changed_creds(self):
        # changed credentials are respected
        config = get_config(path=None)
        config["DEFAULT"]["waeup_user"] = "foo"
        config["DEFAULT"]["waeup_passwd"] = "bar"
        assert get_url_from_config(config) == "https://foo:bar@localhost:8080"

    def test_get_url_from_config_with_paths(self):
        # app paths are taken into account
        config = get_config(path=None)
        config["DEFAULT"]["waeup_url"] = "http://sample.org/app"
        assert get_url_from_config(config) == (
            "http://grok:grok@sample.org/app")


def test_waeup_server_fixture_works(waeup_server):
    # We can reac
    proxy = xmlrpcclient.ServerProxy(
        "http://mgr:mgrpw@localhost:61614")
    assert proxy.ping(42) == ['pong', 42]


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
        self.proxy = xmlrpcclient.ServerProxy(
            "http://mgr:mgrpw@localhost:61615")
        self.proxy.reset_student_db()

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def populate_db(self):
        # create student in db
        self.proxy.create_student(
            'AB123456', "foo@sample.org", "foo", "bar",
            "passport.png", xmlrpcclient.Binary(b"FakedPNGFile"),
            {
                "1": xmlrpcclient.Binary(b"FP1Fake"),
                },
            )

    def test_internal_ping(self):
        # make sure the fake xmlrpc server works
        assert self.proxy.ping(42) == ['pong', 42]

    def test_internal_auth(self):
        # make sure our fake xmlrpc server requires authentication
        proxy = xmlrpcclient.ServerProxy(
            "http://localhost:61615")
        self.assertRaises(
            xmlrpcclient.ProtocolError, proxy.ping, 42)

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
            xmlrpcclient.Fault,
            self.proxy.put_student_fingerprints, 'invalid-id')
        # fingerprint dict not a dict
        self.assertRaises(
            xmlrpcclient.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', 'not-a-dict')
        # invalid fingerprint file type
        self.assertRaises(
            xmlrpcclient.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', {'1': 12})
        # invalid file format
        self.assertRaises(
            xmlrpcclient.Fault,
            self.proxy.put_student_fingerprints, 'AB123456', {
                '1': xmlrpcclient.Binary(b'not-an-fpm-file')}
            )
        # valid fingerprint dict
        assert self.proxy.put_student_fingerprints(
            'AB123456', {
                '1': xmlrpcclient.Binary(b'FP1-faked-fpm-file')}
            ) is True
        # empty fingerprint dict
        assert self.proxy.put_student_fingerprints(
            'AB123456', {}) is False

    def test_internal_get_student_fingerprints(self):
        # the faked get_student_fingerprint method works as
        # as the Kofa original.
        self.populate_db()
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
        assert result is True

    def test_store_fingerprint_unauth(self):
        # tries to store fingerprints unauthorized will be blocked
        self.proxy.create_student('AB123456')
        fpm_file_path = create_fake_fpm_file(self.workdir)
        result = store_fingerprint(
            "http://localhost:61615", "AB123456", 1, fpm_file_path)
        assert result == "Error: 401 Unauthorized"

    def test_store_fingerprint_invalid_server(self):
        # trying to connect to invalid servers will raise socket errors.
        fpm_file_path = create_fake_fpm_file(self.workdir)
        self.assertRaises(socket.error, store_fingerprint,
                          "http://localhost:12345", "AB123456", 1,
                          fpm_file_path)

    def test_get_fingerprints(self):
        # we can retrieve stored fingerprints
        self.populate_db()
        result = get_fingerprints(
            "http://mgr:mgrpw@localhost:61615",
            "AB123456")
        assert isinstance(result, dict)
        assert result.get("email", None) == "foo@sample.org"
        assert result.get("firstname", None) == "foo"
        assert result.get("lastname", None) == "bar"
        assert result.get("img", None) is not None
        img = result["img"].data
        assert img == b"FakedPNGFile"
        assert result.get("img_name", None) == "passport.png"
        assert isinstance(result.get("fingerprints", None), dict)
        fprints = result.get("fingerprints")
        assert "1" in fprints.keys()
        fprint = fprints["1"].data
        assert fprint == b"FP1Fake"

    def test_get_fingerprints_unauth(self):
        # we cannot get fingerprints w/o being authorized
        self.populate_db()
        result = get_fingerprints(
            "http://illegal:mgrpw@localhost:61615",
            "AB123456"
            )
        assert result == "Error: 401 Unauthorized"

    def test_get_fingerprints_invalid_server(self):
        # we cannot get fingerprints w/o being authorized
        self.populate_db()
        self.assertRaises(
            socket.error,
            get_fingerprints,
            "http://illegal:mgrpw@localhost:12345",
            "AB123456"
            )
