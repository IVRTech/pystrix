"""Tests for the FastAGI client handler (`_AGIClientHandler`)."""

import io
import types

import pytest

from pystrix.agi.fastagi import _AGIClientHandler


class _ClosedReader:
    """The read end of a socket whose client has already disconnected."""

    def readline(self):
        return b""  # EOF: nothing was sent before the connection closed


class _EnvReader:
    """Yields a minimal AGI environment block, then EOF."""

    def __init__(self, *lines):
        self._lines = list(lines)
        self._index = 0

    def readline(self):
        if self._index >= len(self._lines):
            return b""
        line = self._lines[self._index]
        self._index += 1
        return line


def _handler(rfile, handler_callable=None):
    # Bypass socketserver's __init__ (which would call handle() itself) and wire
    # up only what handle() touches: the read/write files and the server.
    instance = _AGIClientHandler.__new__(_AGIClientHandler)
    instance.rfile = rfile
    instance.wfile = io.BytesIO()
    instance.client_address = ("198.51.100.7", 51234)
    instance.server = types.SimpleNamespace(
        debug=False,
        get_script_handler=lambda path: (handler_callable, None),
    )
    return instance


def test_handle_returns_quietly_when_client_disconnects_during_handshake():
    # Regression for #49: a client that closes before sending the AGI
    # environment makes the handshake raise AGISIGPIPEHangup. handle() must end
    # the request quietly instead of letting that propagate into a stderr
    # traceback from socketserver.
    invoked = []
    handler = _handler(
        _ClosedReader(), handler_callable=lambda *args: invoked.append(args)
    )

    handler.handle()  # must not raise

    assert invoked == []  # no script handler runs when the client is already gone
    assert handler.wfile.getvalue() == b""  # nothing written back on the quiet path


def test_handle_returns_quietly_when_client_disconnects_mid_handshake():
    # A client that sends part of the environment then drops hits EOF inside the
    # parse loop, not on the first read. Still a handshake hangup that must end
    # the request quietly.
    invoked = []
    reader = _EnvReader(b"agi_network_script: demo\n")  # no blank terminator, then EOF
    handler = _handler(reader, handler_callable=lambda *args: invoked.append(args))

    handler.handle()  # must not raise

    assert invoked == []


def test_handle_propagates_handler_errors():
    # The handshake-hangup suppression is scoped to the environment read only.
    # A genuine error raised by the script handler must still propagate.
    def boom(agi, args, kwargs, match, path):
        raise RuntimeError("handler blew up")

    handler = _handler(
        _EnvReader(b"agi_network_script: demo\n", b"\n"),
        handler_callable=boom,
    )
    with pytest.raises(RuntimeError):
        handler.handle()
