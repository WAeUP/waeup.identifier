# fixtures for py.test.
#
# py.test finds them automatically if put in a file called `conftest.py`.
import pytest
import threading
import xmlrpc.client as xmlrpcclient
from waeup.identifier.testing import AuthenticatingXMLRPCServer


@pytest.fixture(scope="function")
def home_dir(request, monkeypatch, tmpdir):
    """A py.test fixture providing a temporary user home.

    It also sets PATH to contain this temporary home as only entry.
    """
    tmpdir.mkdir("home")
    monkeypatch.setenv("HOME", str(tmpdir / "home"))
    monkeypatch.setenv("PATH", str(tmpdir / "home"))
    return tmpdir / "home"


@pytest.fixture(scope="session")
def waeup_server(request):
    """A py.test fixture that starts an authenticating XMLRPC server.

    The server mimics WAeUP servers' behavior for fingerprint-related
    xmlrpc requests.
    """
    server = AuthenticatingXMLRPCServer("127.0.0.1", 61614)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    request.addfinalizer(server.shutdown)
    return (server, server_thread)


@pytest.fixture(scope="function")
def waeup_proxy(request, waeup_server):
    proxy = xmlrpcclient.ServerProxy(
        "http://mgr:mgrpw@localhost:61614")
    return proxy
