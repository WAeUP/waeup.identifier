# fixtures for py.test.
#
# py.test finds them automatically if put in a file called `conftest.py`.
import pytest


@pytest.fixture(scope="function")
def home_dir(request, monkeypatch, tmpdir):
    """A py.test fixture providing a temporary user home.

    It also sets PATH to contain this temporary home as only entry.
    """
    tmpdir.mkdir("home")
    monkeypatch.setenv("HOME", str(tmpdir / "home"))
    monkeypatch.setenv("PATH", str(tmpdir / "home"))
    return tmpdir / "home"


