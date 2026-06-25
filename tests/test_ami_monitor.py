"""Tests for the AMI connection monitor (`Manager.monitor_connection`)."""

import threading

from pystrix.ami.ami import Manager, ManagerError, ManagerSocketError


def _bare_manager(send_action, is_connected=None):
    # Bypass __init__ so no real socket or reader thread is created. The monitor
    # only touches is_connected() and send_action(), so those are all we supply.
    manager = Manager.__new__(Manager)
    manager.is_connected = is_connected or (lambda: True)
    manager.send_action = send_action
    # The manager was never connected, so its __del__ cleanup has nothing real
    # to release; neutralize it to keep garbage collection quiet during tests.
    manager.close = lambda: None
    return manager


def _run_monitor(manager, interval=0):
    # Run the monitor to completion, capturing anything that escapes the thread
    # uncaught via threading.excepthook. Returns (monitor_thread, unhandled).
    unhandled = []
    previous_hook = threading.excepthook
    threading.excepthook = lambda args: unhandled.append(args)
    try:
        monitor = manager.monitor_connection(interval=interval)
        monitor.join(timeout=2)
    finally:
        threading.excepthook = previous_hook
    return monitor, unhandled


def test_monitor_connection_survives_socket_error():
    # Regression for #3: when Asterisk stops, the periodic Ping's send_action
    # raises ManagerSocketError. The monitor thread must exit cleanly instead of
    # dying with an unhandled exception (a traceback dumped to stderr).
    reached = threading.Event()

    def send_action(request, *args, **kwargs):
        reached.set()
        raise ManagerSocketError("Asterisk service stopped")

    monitor, unhandled = _run_monitor(_bare_manager(send_action))

    assert reached.is_set()  # the monitor actually attempted a ping
    assert not monitor.is_alive()  # the thread terminated
    assert unhandled == []  # nothing escaped the thread uncaught


def test_monitor_connection_survives_manager_error():
    # Race guard for #3: the connection can drop between the loop's is_connected()
    # check and the liveness re-check inside send_action, which raises ManagerError
    # (not ManagerSocketError). The monitor must catch that path too and exit
    # cleanly rather than crash the thread.
    reached = threading.Event()

    def send_action(request, *args, **kwargs):
        reached.set()
        raise ManagerError("Not connected to an Asterisk manager")

    monitor, unhandled = _run_monitor(_bare_manager(send_action))

    assert reached.is_set()
    assert not monitor.is_alive()
    assert unhandled == []


def test_monitor_connection_pings_until_disconnected():
    # The monitor pings on each loop while connected and exits cleanly when
    # is_connected() turns False (the orderly-shutdown path).
    checks = {"count": 0}

    def is_connected():
        checks["count"] += 1
        return checks["count"] <= 3  # connected for three iterations, then down

    pings = []

    def send_action(request, *args, **kwargs):
        pings.append(request)

    manager = _bare_manager(send_action, is_connected=is_connected)
    monitor, unhandled = _run_monitor(manager)

    assert isinstance(monitor, threading.Thread)  # returns a joinable thread
    assert not monitor.is_alive()  # exited on the first disconnected check
    assert len(pings) == 3  # one ping per connected check, none after
    assert unhandled == []


def test_monitor_connection_propagates_unexpected_errors():
    # The catch is deliberately narrow: only connection-loss errors stop the
    # monitor quietly. An unexpected error must still surface (escape the thread)
    # rather than be silently swallowed by a too-broad except.
    def send_action(request, *args, **kwargs):
        raise ValueError("unexpected")

    monitor, unhandled = _run_monitor(_bare_manager(send_action))

    assert not monitor.is_alive()
    assert len(unhandled) == 1  # the ValueError was not swallowed
    assert unhandled[0].exc_type is ValueError
