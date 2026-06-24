"""Tests for AMI request building (`pystrix.ami.ami._Request`)."""
import pytest

from pystrix.ami.ami import _Request


def _build(request, action_id=None, **kwargs):
    return request.build_request(action_id, lambda: 'GEN-1', **kwargs)


def test_generates_action_id_when_absent():
    command, action_id = _build(_Request('Ping'))
    assert action_id == 'GEN-1'
    assert command == 'Action: Ping\r\nActionID: GEN-1\r\n\r\n'


def test_uses_explicit_action_id():
    command, action_id = _build(_Request('Ping'), action_id='custom')
    assert action_id == 'custom'
    assert 'ActionID: custom' in command


def test_action_is_always_the_first_line():
    request = _Request('Login')
    request['Username'] = 'admin'
    command, _ = _build(request)
    assert command.startswith('Action: Login\r\n')


def test_multi_value_header_expands_to_repeated_lines():
    request = _Request('Originate')
    request['Variable'] = ('a=1', 'b=2')
    command, _ = _build(request)
    assert 'Variable: a=1\r\n' in command
    assert 'Variable: b=2\r\n' in command


def test_multi_value_order_preserved_and_blank_line_terminator():
    request = _Request('Originate')
    request['Variable'] = ('a=1', 'b=2')
    command, _ = _build(request)
    assert command.index('Variable: a=1') < command.index('Variable: b=2')
    assert command.endswith('\r\n\r\n')


def test_kwargs_become_headers():
    command, _ = _build(_Request('Ping'), Extra='x')
    assert 'Extra: x' in command


# The two cases below encode build_request's documented ActionID contract.
# The implementation currently violates it (see issue #43): a pre-set ActionID
# is dropped when action_id is None, and it overrides an explicit action_id.
# These are strict xfails, so they will fail loudly once #43 is fixed, prompting
# removal of the markers.
@pytest.mark.xfail(reason="build_request drops a pre-set ActionID; see #43", strict=True)
def test_preset_action_id_used_when_none_passed():
    request = _Request('Ping')
    request['ActionID'] = 'preset'
    command, action_id = _build(request)
    assert action_id == 'preset'
    assert 'ActionID: preset' in command


@pytest.mark.xfail(reason="explicit action_id loses to a pre-set ActionID; see #43", strict=True)
def test_explicit_action_id_wins_over_preset():
    request = _Request('Ping')
    request['ActionID'] = 'preset'
    command, action_id = _build(request, action_id='explicit')
    assert action_id == 'explicit'
    assert 'ActionID: explicit' in command
