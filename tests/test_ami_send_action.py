"""Tests for `Manager.send_action` connection-loss handling."""

import threading

import pytest

from pystrix.ami import core
from pystrix.ami.ami import Manager, ManagerSocketError


def test_send_action_raises_when_connection_closed_mid_send():
    # Race guard (#3): a concurrent disconnect() can clear _connection after
    # send_action's liveness check but before the send. send_action must raise
    # ManagerSocketError rather than dereferencing None with an AttributeError,
    # which the connection monitor's catch would miss and crash the thread.
    manager = Manager.__new__(Manager)
    manager.is_connected = lambda: True
    manager._connection = None  # disconnect() raced in and cleared it
    manager._connection_lock = threading.Lock()
    manager._outstanding_requests = {}
    # Never connected, so neutralize __del__ cleanup to keep GC quiet.
    manager.close = lambda: None

    with pytest.raises(ManagerSocketError):
        manager.send_action(core.Ping(), action_id="race-1")

    # The request registered just before the failed send is dropped again.
    assert manager._outstanding_requests == {}
