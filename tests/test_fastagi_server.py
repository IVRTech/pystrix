"""Tests for FastAGIServer listen-backlog configuration."""

from pystrix.agi.fastagi import FastAGIServer, _ThreadedTCPServer


def test_server_requests_max_listen_backlog():
    # Regression for #32: the server asks for the largest backlog the socket
    # call accepts and lets the kernel cap it to the live somaxconn. Binding on
    # an ephemeral port also proves the platform's listen() accepts the value
    # rather than rejecting it.
    server = FastAGIServer(interface="127.0.0.1", port=0)
    try:
        assert server.request_queue_size == 2**31 - 1
    finally:
        server.server_close()


def test_backlog_sizing_does_not_shell_out():
    # The sysctl-spawning, OS-branching helper is gone; backlog sizing no longer
    # shells out or raises on platforms without sysctl (regression for #32).
    assert not hasattr(_ThreadedTCPServer, "get_somaxconn")
