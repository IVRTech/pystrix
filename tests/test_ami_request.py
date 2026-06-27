"""Tests for AMI request building (`pystrix.ami.ami._Request`)."""

import pytest

from pystrix.ami.ami import _Request
from pystrix.ami.core import Originate_Application


def _build(request, action_id=None, **kwargs):
    return request.build_request(action_id, lambda: "GEN-1", **kwargs)


def test_generates_action_id_when_absent():
    command, action_id = _build(_Request("Ping"))
    assert action_id == "GEN-1"
    assert command == "Action: Ping\r\nActionID: GEN-1\r\n\r\n"


def test_uses_explicit_action_id():
    command, action_id = _build(_Request("Ping"), action_id="custom")
    assert action_id == "custom"
    assert "ActionID: custom" in command


def test_action_is_always_the_first_line():
    request = _Request("Login")
    request["Username"] = "admin"
    command, _ = _build(request)
    assert command.startswith("Action: Login\r\n")


def test_multi_value_header_expands_to_repeated_lines():
    request = _Request("Originate")
    request["Variable"] = ("a=1", "b=2")
    command, _ = _build(request)
    assert "Variable: a=1\r\n" in command
    assert "Variable: b=2\r\n" in command


def test_originate_application_treats_string_data_as_one_argument():
    request = Originate_Application("SIP/708", "Playback", "goodbye")

    command, _ = _build(request)

    assert "Data: goodbye\r\n" in command
    assert "Data: g,o,o,d,b,y,e\r\n" not in command


def test_originate_application_preserves_sequence_data_arguments():
    request = Originate_Application("SIP/708", "Playback", ("goodbye", "noanswer"))

    command, _ = _build(request)

    assert "Data: goodbye,noanswer\r\n" in command


@pytest.mark.parametrize(
    "data",
    [
        b"goodbye",
        b"",
        bytearray(b"goodbye"),
        bytearray(),
        memoryview(b"goodbye"),
        memoryview(b""),
    ],
)
def test_originate_application_rejects_binary_data(data):
    with pytest.raises(
        TypeError, match="data must be a string or sequence of strings, not bytes"
    ):
        Originate_Application("SIP/708", "Playback", data)


def test_originate_application_omits_empty_string_data():
    request = Originate_Application("SIP/708", "Playback", "")

    command, _ = _build(request)

    assert "Data:" not in command


def test_rejects_header_value_containing_crlf():
    request = _Request("Originate")
    request["Data"] = "goodbye\r\nInjected: x"

    with pytest.raises(ValueError, match="AMI header values must not contain CR or LF"):
        _build(request)


def test_rejects_action_value_containing_crlf():
    request = _Request("Ping\r\nInjected: x")

    with pytest.raises(ValueError, match="AMI header values must not contain CR or LF"):
        _build(request)


def test_rejects_header_key_containing_crlf():
    request = _Request("Originate")
    request["Data\r\nInjected"] = "goodbye"

    with pytest.raises(ValueError, match="AMI header keys must not contain CR or LF"):
        _build(request)


def test_rejects_multi_value_header_value_containing_crlf():
    request = _Request("Originate")
    request["Variable"] = ("a=1\r\nInjected: x", "b=2")

    with pytest.raises(ValueError, match="AMI header values must not contain CR or LF"):
        _build(request)


def test_rejects_action_id_containing_crlf():
    request = _Request("Ping")

    with pytest.raises(ValueError, match="AMI header values must not contain CR or LF"):
        _build(request, action_id="safe\r\nInjected: x")


def test_multi_value_order_preserved_and_blank_line_terminator():
    request = _Request("Originate")
    request["Variable"] = ("a=1", "b=2")
    command, _ = _build(request)
    assert command.index("Variable: a=1") < command.index("Variable: b=2")
    assert command.endswith("\r\n\r\n")


def test_kwargs_become_headers():
    command, _ = _build(_Request("Ping"), Extra="x")
    assert "Extra: x" in command


# build_request resolves the ActionID with the precedence documented on the
# method: an explicit argument wins, then a value already set on the request,
# then a generated one (fixed in #43).
def test_preset_action_id_used_when_none_passed():
    request = _Request("Ping")
    request["ActionID"] = "preset"
    command, action_id = _build(request)
    assert action_id == "preset"
    assert "ActionID: preset" in command


def test_explicit_action_id_wins_over_preset():
    request = _Request("Ping")
    request["ActionID"] = "preset"
    command, action_id = _build(request, action_id="explicit")
    assert action_id == "explicit"
    assert "ActionID: explicit" in command


def test_non_string_action_id_is_stringified():
    # A non-string ActionID must be returned as a string so it matches the
    # string-keyed responses Asterisk sends back (see #43 review).
    request = _Request("Ping")
    request["ActionID"] = 7
    command, action_id = _build(request)
    assert action_id == "7"
    assert "ActionID: 7" in command
