import pytest
try:
    import xmlrpc.client as xmlrpcclient   # Python 3.x
except ImportError:                        # pragma: no cover
    import xmlrpclib as xmlrpcclient       # Python 2.x
from waeup.identifier.testing import create_fake_fpm_file
from waeup.identifier.webservice import (
    store_fingerprint, get_fingerprints, get_url
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


class TestWebservice(object):

    def populate_db(self, proxy):
        # create student in db
        proxy.create_student(
            'AB123456', "foo@sample.org", "foo", "bar",
            "passport.png", xmlrpcclient.Binary(b"FakedPNGFile"),
            {
                "1": xmlrpcclient.Binary(b"FP1Fake"),
                },
            )

    def test_waeup_server_fixture_works(self, waeup_server):
        # Ensure there is a (fake) waeup server running  in background.
        # Should be started by `waeup_server` fixture once per session.
        proxy = xmlrpcclient.ServerProxy(
            "http://mgr:mgrpw@localhost:61614")
        assert proxy.ping(42) == ['pong', 42]

    def test_waeup_proxy_fixture_works(self, waeup_proxy):
        # Ensure wecan get a working XMLRPC server proxy
        assert waeup_proxy.ping(42) == ['pong', 42]

    def test_internal_auth(self, waeup_server):
        # make sure our fake xmlrpc server requires authentication
        proxy = xmlrpcclient.ServerProxy(
            "http://localhost:61614")
        with pytest.raises(xmlrpcclient.ProtocolError):
            proxy.ping(42)

    def test_internal_methods(self, waeup_proxy):
        # the following methods are available
        assert sorted(waeup_proxy.system.listMethods()) == [
            'create_student',
            'get_student_fingerprints', 'ping',
            'put_student_fingerprints',
            'reset_student_db', 'system.listMethods',
            'system.methodHelp', 'system.methodSignature']

    def test_internal_put_student_fingerprints(self, waeup_proxy):
        # make sure the faked method is faked properly
        waeup_proxy.create_student('AB123456')
        # invalid student id
        with pytest.raises(xmlrpcclient.Fault):
            waeup_proxy.put_student_fingerprints('invalid-id')
        # fingerprint dict not a dict
        with pytest.raises(xmlrpcclient.Fault):
            waeup_proxy.put_student_fingerprints('AB123456', 'not-a-dict')
        # invalid fingerprint file type
        with pytest.raises(xmlrpcclient.Fault):
            waeup_proxy.put_student_fingerprints('AB123456', {'1': 12})
        # invalid file format
        with pytest.raises(xmlrpcclient.Fault):
            waeup_proxy.put_student_fingerprints(
                'AB123456', {'1': xmlrpcclient.Binary(b'not-an-fpm-file')})
        # valid fingerprint dict
        assert waeup_proxy.put_student_fingerprints(
            'AB123456', {'1': xmlrpcclient.Binary(b'FP1-faked-fpm-file')}
            ) is True
        # empty fingerprint dict
        assert waeup_proxy.put_student_fingerprints('AB123456', {}) is False

    def test_internal_get_student_fingerprints(self, waeup_proxy):
        # the faked get_student_fingerprint method works as
        # as the Kofa original.
        self.populate_db(waeup_proxy)
        result1 = waeup_proxy.get_student_fingerprints("InvalidID")
        assert result1 == dict()
        result2 = waeup_proxy.get_student_fingerprints("AB123456")
        assert isinstance(result2, dict)
        assert result2["email"] == "foo@sample.org"
        assert result2["firstname"] == "foo"
        assert result2["lastname"] == "bar"
        assert result2["img_name"] == "passport.png"
        assert result2["img"].data == b"FakedPNGFile"
        assert result2["fingerprints"]["1"].data == b"FP1Fake"

    def test_store_fingerprint(self, waeup_proxy, tmpdir):
        # we can store a fingerprint
        waeup_proxy.create_student('AB123456')
        fpm_file_path = create_fake_fpm_file(str(tmpdir))
        result = store_fingerprint(
            "http://mgr:mgrpw@localhost:61614", "AB123456", 1, fpm_file_path)
        assert result is True

    def test_store_fingerprint_unauth(self, waeup_proxy, tmpdir):
        # tries to store fingerprints unauthorized will be blocked
        waeup_proxy.create_student('AB123456')
        fpm_file_path = create_fake_fpm_file(str(tmpdir))
        result = store_fingerprint(
            "http://localhost:61614", "AB123456", 1, fpm_file_path)
        assert result == "Error: 401 Unauthorized"

    def test_store_fingerprint_invalid_server(self, tmpdir):
        # trying to connect to invalid servers will raise socket errors.
        fpm_file_path = create_fake_fpm_file(str(tmpdir))
        result = store_fingerprint(
            "http://localhost:12345", "AB123456", 1, fpm_file_path)
        assert result == "Error: [Errno 111] Connection refused"

    def test_get_fingerprints(self, waeup_proxy):
        # we can retrieve stored fingerprints
        self.populate_db(waeup_proxy)
        result = get_fingerprints(
            "http://mgr:mgrpw@localhost:61614", "AB123456")
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

    def test_get_fingerprints_unauth(self, waeup_proxy):
        # we cannot get fingerprints w/o being authorized
        self.populate_db(waeup_proxy)
        result = get_fingerprints(
            "http://illegal:mgrpw@localhost:61614", "AB123456")
        assert result == "Error: 401 Unauthorized"

    def test_get_fingerprints_invalid_server(self, waeup_proxy):
        # trying to connect to invalid servers will raise socket errors.
        self.populate_db(waeup_proxy)
        result = get_fingerprints(
            "http://mgr:mgrpw@localhost:12345", "AB123456")
        assert result == "Error: [Errno 111] Connection refused"
