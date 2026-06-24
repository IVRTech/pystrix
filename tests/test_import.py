"""Import smoke tests that double as a cross-version compatibility check."""


def test_package_imports():
    import pystrix

    assert pystrix.VERSION


def test_public_entry_points_import():
    from pystrix.agi import AGI, FastAGI, FastAGIServer
    from pystrix.agi.fastagi import FastAGIServer as _FastAGIServer
    from pystrix.ami import Manager

    # The re-export must be the same class object, and importing fastagi
    # exercises the code path that has to stay free of the cgi module removed in
    # Python 3.13.
    assert FastAGIServer is _FastAGIServer
    assert (
        isinstance(AGI, type)
        and isinstance(FastAGI, type)
        and isinstance(Manager, type)
    )
