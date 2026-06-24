"""Tests for AGI response parsing and helpers (`pystrix.agi.agi_core`)."""

import pytest

from pystrix.agi.agi_core import (
    _AGI,
    AGIDeadChannelError,
    AGIInvalidCommandError,
    AGINoResultError,
    AGIResultHangup,
    AGIUnknownError,
    AGIUsageError,
    _Action,
    quote,
)
from pystrix.agi.core import GetData


class _FakeReader:
    """A minimal stand-in for the read end of the Asterisk pipe."""

    def __init__(self, *lines):
        self._lines = [line.encode() for line in lines]
        self._index = 0

    def readline(self):
        if self._index >= len(self._lines):
            return b""
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
    response = _agi("200 result=1\n")._get_result()
    assert response.code == 200
    assert response.items["result"].value == "1"


def test_parses_result_data():
    response = _agi("200 result=1 (speech)\n")._get_result()
    assert response.items["result"].value == "1"
    assert response.items["result"].data == "speech"


def test_result_without_parenthetical_has_empty_data():
    # A result with no parenthetical reports data as '' (empty string), not None.
    response = _agi("200 result=1\n")._get_result()
    assert response.items["result"].data == ""


def test_usage_error_collects_multiline_block():
    # The 520 path reads lines until '520 End of proper usage.' and raises with
    # the accumulated block.
    with pytest.raises(AGIUsageError) as exc_info:
        _agi(
            "520 Invalid command syntax.\n",
            "Usage: ANSWER\n",
            "520 End of proper usage.\n",
        )._get_result()
    message = str(exc_info.value)
    assert "520 Invalid command syntax." in message
    assert "Usage: ANSWER" in message


def test_unrecognized_code_returns_none():
    # A line with no leading status code (for example after a signal) yields no
    # result rather than raising.
    assert _agi("\n")._get_result() is None


def test_unknown_code_raises():
    with pytest.raises(AGIUnknownError):
        _agi("418 unexpected\n")._get_result()


def test_hangup_detected_by_data_not_value():
    # The hangup guard keys on the parenthetical data, not the result value, so a
    # non-(-1) value with 'hangup' data must still raise.
    with pytest.raises(AGIResultHangup):
        _agi("200 result=0 (hangup)\n")._get_result()


def test_hangup_not_raised_when_check_disabled():
    response = _agi("200 result=-1 (hangup)\n")._get_result(check_hangup=False)
    assert response.items["result"].data == "hangup"


def test_invalid_command_raises():
    with pytest.raises(AGIInvalidCommandError):
        _agi("510 Invalid or unknown command\n")._get_result()


def test_dead_channel_raises():
    with pytest.raises(AGIDeadChannelError):
        _agi("511 Command Not Permitted on a dead channel\n")._get_result()


def test_missing_result_key_raises():
    with pytest.raises(AGINoResultError):
        _agi("200 foo=bar\n")._get_result()


def test_hangup_result_raises():
    with pytest.raises(AGIResultHangup):
        _agi("200 result=-1 (hangup)\n")._get_result()


def test_action_command_formatting():
    assert _Action("ANSWER").command == "ANSWER\n"
    # None arguments are dropped and a trailing newline is always present.
    assert _Action("STREAM FILE", "demo", None, "#").command == "STREAM FILE demo #\n"


def test_quote_wraps_in_double_quotes():
    assert quote("demo") == '"demo"'
    assert quote(5) == '"5"'


class _StrReader:
    """A reader that yields str lines, as plain AGI's stdin does."""

    def __init__(self, *lines):
        self._lines = list(lines)
        self._index = 0

    def readline(self):
        if self._index >= len(self._lines):
            return ""
        line = self._lines[self._index]
        self._index += 1
        return line


def _agi_with_reader(reader):
    agi = _AGI.__new__(_AGI)
    agi._environment = {}
    agi._rfile = reader
    return agi


def test_str_input_is_read_without_decoding():
    # Plain AGI reads str from stdin; _read_line must not choke trying to decode it.
    response = _agi_with_reader(_StrReader("200 result=1\n"))._get_result()
    assert response.items["result"].value == "1"


def test_malformed_bytes_surface_a_decode_error():
    # A real decode failure on socket bytes propagates instead of being swallowed.
    class _BadBytesReader:
        def readline(self):
            return b"\xff\xfe not utf-8\n"

    with pytest.raises(UnicodeDecodeError):
        _agi_with_reader(_BadBytesReader())._get_result()


def test_getdata_timeout_result_parses_without_error():
    # Regression for #9 (fixed in 12c4bd7, 2014): a GetData timeout replies
    # "result= (timeout)" with an empty value before the parenthetical. It must
    # parse as value '' / data 'timeout', not raise AGINoResultError.
    response = _agi("200 result= (timeout)\n")._get_result()
    assert response.items["result"].value == ""
    assert response.items["result"].data == "timeout"


def test_getdata_process_response_flags_timeout():
    response = _agi("200 result= (timeout)\n")._get_result()
    keys, timed_out = GetData("prompt").process_response(response)
    assert keys == ""
    assert timed_out is True


def test_getdata_process_response_returns_digits():
    response = _agi("200 result=1234\n")._get_result()
    keys, timed_out = GetData("prompt").process_response(response)
    assert keys == "1234"
    assert timed_out is False


def test_getdata_process_response_keeps_partial_digits_on_timeout():
    # The common real-world timeout: a caller enters some digits, then the
    # inter-digit timer expires. Asterisk replies "result=12 (timeout)", so the
    # collected digits and the timeout flag must both survive process_response.
    response = _agi("200 result=12 (timeout)\n")._get_result()
    keys, timed_out = GetData("prompt").process_response(response)
    assert keys == "12"
    assert timed_out is True
