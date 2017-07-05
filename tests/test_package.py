import waeup.identifier

def test_have_version():
    # we have a version number.
    assert hasattr(waeup.identifier, '__version__')
