"""Tests for FastAGIServer listen-backlog configuration."""

from pystrix.agi import fastagi
from pystrix.agi.fastagi import _LISTEN_BACKLOG, FastAGIServer, _ThreadedTCPServer


def test_server_requests_max_listen_backlog():
    # Regression for #32: the server asks for the largest backlog the socket
    # call accepts and lets the kernel cap it to the live somaxconn. Binding on
    # an ephemeral port also proves the platform's listen() accepts the value
    # rather than rejecting it.
    server = FastAGIServer(interface="127.0.0.1", port=0)
    try:
        assert server.request_queue_size == _LISTEN_BACKLOG
        # A fixed ceiling like 65535 could undershoot a tuned-up somaxconn; the
        # backlog must exceed it so the kernel's own limit is the only cap.
        assert _LISTEN_BACKLOG > 65535
    finally:
        server.server_close()


def test_backlog_sizing_does_not_shell_out():
    # The sysctl-spawning, OS-branching helper is gone and the module no longer
    # imports the subprocess/platform machinery it used, so backlog sizing cannot
    # shell out or raise on platforms without sysctl (regression for #32).
    assert not hasattr(_ThreadedTCPServer, "get_somaxconn")
    assert not hasattr(fastagi, "subprocess")
    assert not hasattr(fastagi, "platform")
