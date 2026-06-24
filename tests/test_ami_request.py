"""Tests for AMI request building (`pystrix.ami.ami._Request`)."""
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


def test_kwargs_become_headers():
    command, _ = _build(_Request('Ping'), Extra='x')
    assert 'Extra: x' in command
