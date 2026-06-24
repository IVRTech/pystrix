"""Import smoke tests that double as a cross-version compatibility check."""


def test_package_imports():
    import pystrix
    assert pystrix.VERSION


def test_public_entry_points_import():
    from pystrix.agi import AGI, FastAGIServer, FastAGI
    from pystrix.ami import Manager

    # Importing FastAGIServer exercises pystrix/agi/fastagi.py, which must not
    # pull in the cgi module that Python 3.13 removed.
    assert AGI and FastAGIServer and FastAGI and Manager
