"""Tests for `Manager.send_action` connection-loss handling."""

import threading

import pytest

from pystrix.ami import core
from pystrix.ami.ami import Manager, ManagerSocketError, _Request


class _SynchronousRequest(_Request):
    # A request that registers a (events, finalisers) entry rather than the
    # plain None an asynchronous request stores. No shipped request sets
    # synchronous = True, so define a minimal one to exercise that branch.
    synchronous = True


def _bare_manager(connection):
    # Bypass __init__ and supply only what send_action touches; neutralize
    # __del__ cleanup to keep GC quiet. is_connected() reports True so the
    # send path runs; the supplied connection decides how the send behaves.
    manager = Manager.__new__(Manager)
    manager.is_connected = lambda: True
    manager._connection = connection
    manager._connection_lock = threading.Lock()
    manager._outstanding_requests = {}
    manager.close = lambda: None
    return manager


def _disconnected_manager():
    # A raced disconnect() already cleared _connection while is_connected()
    # still reports True.
    return _bare_manager(None)


class _FailingConnection:
    # A connection whose send fails mid-write, as a real socket does when it
    # breaks during transmission.
    def send_message(self, command):
        raise ManagerSocketError("Connection to Asterisk manager broken while sending")


def test_send_action_raises_when_connection_closed_mid_send():
    # Race guard (#3): a concurrent disconnect() can clear _connection after
    # send_action's liveness check but before the send. send_action must raise
    # ManagerSocketError rather than dereferencing None with an AttributeError,
    # which the connection monitor's catch would miss and crash the thread.
    manager = _disconnected_manager()

    with pytest.raises(ManagerSocketError):
        manager.send_action(core.Ping(), action_id="race-1")

    # The request registered just before the failed send is dropped again.
    assert manager._outstanding_requests == {}


def test_send_action_drops_synchronous_request_when_connection_closed_mid_send():
    # The same race for a synchronous request, whose tracking entry is a
    # (events, finalisers) tuple rather than None. The cleanup must drop it too,
    # so a synchronous caller cannot be left waiting on events that never arrive.
    manager = _disconnected_manager()

    with pytest.raises(ManagerSocketError):
        manager.send_action(_SynchronousRequest("Test"), action_id="race-2")

    assert manager._outstanding_requests == {}


def test_send_action_drops_request_when_send_fails_mid_write():
    # If the socket breaks during send_message, send_action must drop the
    # request it just registered before re-raising, so it does not linger in
    # _outstanding_requests with no response ever coming.
    manager = _bare_manager(_FailingConnection())

    with pytest.raises(ManagerSocketError):
        manager.send_action(core.Ping(), action_id="send-fail-1")

    assert manager._outstanding_requests == {}


def test_send_action_drops_synchronous_request_when_send_fails_mid_write():
    # The same cleanup for a synchronous request, whose tracking entry is a
    # (events, finalisers) tuple rather than None.
    manager = _bare_manager(_FailingConnection())

    with pytest.raises(ManagerSocketError):
        manager.send_action(_SynchronousRequest("Test"), action_id="send-fail-2")

    assert manager._outstanding_requests == {}
