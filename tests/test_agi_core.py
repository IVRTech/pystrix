"""Tests for AGI response parsing and helpers (`pystrix.agi.agi_core`)."""
import pytest

from pystrix.agi.agi_core import (
    _AGI, _Action, quote,
    AGIInvalidCommandError, AGIDeadChannelError, AGIResultHangup, AGINoResultError,
)


class _FakeReader:
    """A minimal stand-in for the read end of the Asterisk pipe."""

    def __init__(self, *lines):
        self._lines = [line.encode() for line in lines]
        self._index = 0

    def readline(self):
        if self._index >= len(self._lines):
            return b''
        line = self._lines[self._index]
        self._index += 1
        return line


def _agi(*lines):
    # Bypass __init__ so the constructor does not try to read an AGI environment.
    agi = _AGI.__new__(_AGI)
    agi._environment = {}
    agi._rfile = _FakeReader(*lines)
    return agi


def test_parses_success_result():
    response = _agi('200 result=1\n')._get_result()
    assert response.code == 200
    assert response.items['result'].value == '1'


def test_parses_result_data():
    response = _agi('200 result=1 (speech)\n')._get_result()
    assert response.items['result'].value == '1'
    assert response.items['result'].data == 'speech'


def test_invalid_command_raises():
    with pytest.raises(AGIInvalidCommandError):
        _agi('510 Invalid or unknown command\n')._get_result()


def test_dead_channel_raises():
    with pytest.raises(AGIDeadChannelError):
        _agi('511 Command Not Permitted on a dead channel\n')._get_result()


def test_missing_result_key_raises():
    with pytest.raises(AGINoResultError):
        _agi('200 foo=bar\n')._get_result()


def test_hangup_result_raises():
    with pytest.raises(AGIResultHangup):
        _agi('200 result=-1 (hangup)\n')._get_result()


def test_action_command_formatting():
    assert _Action('ANSWER').command == 'ANSWER\n'
    # None arguments are dropped and a trailing newline is always present.
    assert _Action('STREAM FILE', 'demo', None, '#').command == 'STREAM FILE demo #\n'


def test_quote_wraps_in_double_quotes():
    assert quote('demo') == '"demo"'
    assert quote(5) == '"5"'
