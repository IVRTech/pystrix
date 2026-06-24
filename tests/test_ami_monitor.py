"""Tests for the AMI connection monitor (`Manager.monitor_connection`)."""

import threading

from pystrix.ami.ami import Manager, ManagerSocketError


def _bare_manager(send_action):
    # Bypass __init__ so no real socket or reader thread is created. The monitor
    # only touches is_connected() and send_action(), so those are all we supply.
    manager = Manager.__new__(Manager)
    manager.is_connected = lambda: True
    manager.send_action = send_action
    # The manager was never connected, so its __del__ cleanup has nothing real
    # to release; neutralize it to keep garbage collection quiet during tests.
    manager.close = lambda: None
    return manager


def test_monitor_connection_survives_socket_error():
    # Regression for #3: when Asterisk stops, the periodic Ping's send_action
    # raises ManagerSocketError. The monitor thread must exit cleanly instead of
    # dying with an unhandled exception (a traceback dumped to stderr).
    reached = threading.Event()

    def send_action(request, *args, **kwargs):
        reached.set()
        raise ManagerSocketError("Asterisk service stopped")

    manager = _bare_manager(send_action)

    unhandled = []
    previous_hook = threading.excepthook
    threading.excepthook = lambda args: unhandled.append(args)
    try:
        monitor = manager.monitor_connection(interval=0)
        monitor.join(timeout=2)
    finally:
        threading.excepthook = previous_hook

    assert reached.is_set()  # the monitor actually attempted a ping
    assert not monitor.is_alive()  # the thread terminated
    assert unhandled == []  # nothing escaped the thread uncaught
