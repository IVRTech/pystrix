"""Tests for AMI message parsing (`pystrix.ami.ami._Message`)."""
from pystrix.ami.ami import _Message, RESPONSE_GENERIC, EVENT_GENERIC


def _message(*lines):
    # Asterisk sends CRLF-terminated lines, which `read_message` collects into a
    # list before constructing a `_Message`. Reproduce that here.
    return _Message([line + '\r\n' for line in lines])


def test_parses_headers():
    message = _message('Response: Success', 'ActionID: abc-1')
    assert message['Response'] == 'Success'
    assert message['ActionID'] == 'abc-1'
    assert message.action_id == 'abc-1'


def test_name_prefers_event_then_response():
    assert _message('Event: Hangup', 'ActionID: 1').name == 'Hangup'
    assert _message('Response: Success').name == 'Success'


def test_name_prefers_event_when_both_present():
    # `name` is Event or Response, so Event wins when a message carries both.
    assert _message('Event: Hangup', 'Response: Success').name == 'Hangup'


def test_equality_against_string_uses_name():
    assert _message('Event: Hangup') == 'Hangup'


def test_data_payload_follows_headers():
    message = _message('Response: Follows', 'raw output line without a colon')
    assert message['Response'] == 'Follows'
    assert message.data == ['raw output line without a colon']


def test_data_mode_is_sticky_for_later_colon_lines():
    # Once a data line is seen, later colon-bearing lines stay data and are not
    # parsed as headers.
    message = _message('Response: Follows', 'first data line', 'Looks: like-a-header')
    assert message['Response'] == 'Follows'
    assert message.data == ['first data line', 'Looks: like-a-header']
    assert 'Looks' not in message


def test_fake_eol_line_starts_data_section():
    # A line ending in the fake-EOL pattern marks the start of the data section.
    message = _Message(['Response: Follows\r\n', 'payload\n\r\n'])
    assert message['Response'] == 'Follows'
    assert message.data == ['payload']


def test_non_crlf_line_starts_data_section():
    # A line not terminated by CRLF is treated as data, not a header.
    message = _Message(['Response: Follows\r\n', 'payload\n'])
    assert message['Response'] == 'Follows'
    assert message.data == ['payload']


def test_generic_response_when_only_action_id():
    # A reply with an ActionID but no Response header is salvaged as generic.
    assert _message('ActionID: 7')['Response'] == RESPONSE_GENERIC


def test_generic_event_when_unsolicited():
    # A message with neither Response, Event, nor ActionID is a generic event.
    assert _message('Foo: bar')['Event'] == EVENT_GENERIC
